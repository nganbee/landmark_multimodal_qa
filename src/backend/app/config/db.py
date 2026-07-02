import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")

def get_connection():
    """Returns a new connection to the Supabase PostgreSQL database."""
    if not SUPABASE_URL:
        print("WARNING: SUPABASE_URL is not set.")
        return None
    try:
        conn = psycopg2.connect(SUPABASE_URL)
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

def init_db():
    """Creates the request_logs table if it does not exist."""
    conn = get_connection()
    if not conn:
        return
        
    try:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS request_logs (
                    id SERIAL PRIMARY KEY,
                    request_id TEXT UNIQUE NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    endpoint TEXT NOT NULL,
                    latency_ms REAL NOT NULL,
                    landmark_name TEXT,
                    confidence REAL,
                    success BOOLEAN NOT NULL,
                    user_feedback BOOLEAN,
                    ground_truth TEXT
                );
            """)
        conn.commit()
        print("Database initialized: request_logs table is ready.")
    except Exception as e:
        print(f"Error initializing database: {e}")
    finally:
        conn.close()

def log_request(request_id: str, endpoint: str, latency_ms: float, landmark_name: str, confidence: float, success: bool):
    """Logs a request into the database."""
    conn = get_connection()
    if not conn:
        return
        
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO request_logs (request_id, endpoint, latency_ms, landmark_name, confidence, success)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (request_id, endpoint, latency_ms, landmark_name, confidence, success))
        conn.commit()
    except Exception as e:
        print(f"Error logging request: {e}")
    finally:
        conn.close()

def log_feedback(request_id: str, is_correct: bool, actual_landmark: str = None):
    """Updates the user feedback for a specific request log."""
    conn = get_connection()
    if not conn:
        return {"success": False, "error": "Database connection failed"}
        
    try:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE request_logs 
                SET user_feedback = %s, ground_truth = %s 
                WHERE request_id = %s
            """, (is_correct, actual_landmark, request_id))
            
            if cur.rowcount == 0:
                return {"success": False, "error": "Request ID not found"}
                
        conn.commit()
        return {"success": True}
    except Exception as e:
        print(f"Error logging feedback: {e}")
        return {"success": False, "error": str(e)}
    finally:
        conn.close()

def get_dashboard_metrics():
    """Calculates overall metrics for the dashboard, including proxy metrics for degradation."""
    conn = get_connection()
    if not conn:
        return {}
        
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # General Metrics + Accuracy
            cur.execute("""
                SELECT 
                    COUNT(*) as total_requests,
                    AVG(latency_ms) as avg_latency_ms,
                    AVG(confidence) as avg_confidence,
                    SUM(CASE WHEN success THEN 1 ELSE 0 END)::float / GREATEST(COUNT(*), 1) * 100 as success_rate_percent,
                    SUM(CASE WHEN user_feedback = TRUE THEN 1 ELSE 0 END)::float / GREATEST(SUM(CASE WHEN user_feedback IS NOT NULL THEN 1 ELSE 0 END), 1) * 100 as feedback_accuracy_percent,
                    COUNT(user_feedback) as total_feedback_received,
                    SUM(CASE WHEN landmark_name = 'Unknown' OR landmark_name ILIKE '%Outside scope%' THEN 1 ELSE 0 END)::float / GREATEST(COUNT(*), 1) * 100 as unknown_rate_percent
                FROM request_logs
            """)
            metrics = cur.fetchone()
            
            # Additional metrics: top failures (where user said it was wrong and provided a ground truth)
            cur.execute("""
                SELECT ground_truth as actual_landmark, COUNT(*) as fail_count 
                FROM request_logs 
                WHERE user_feedback = FALSE AND ground_truth IS NOT NULL
                GROUP BY ground_truth 
                ORDER BY fail_count DESC 
                LIMIT 5
            """)
            metrics['top_failures'] = cur.fetchall()
            
            # Top detected landmarks
            cur.execute("""
                SELECT landmark_name, COUNT(*) as count 
                FROM request_logs 
                WHERE landmark_name IS NOT NULL AND landmark_name != 'Unknown' 
                GROUP BY landmark_name 
                ORDER BY count DESC 
                LIMIT 5
            """)
            metrics['top_landmarks'] = cur.fetchall()
            
            # Hourly request volume (last 24 hours, converted to UTC+7)
            cur.execute("""
                SELECT 
                    DATE_TRUNC('hour', created_at AT TIME ZONE 'Asia/Ho_Chi_Minh') as hour,
                    COUNT(*) as count
                FROM request_logs
                WHERE created_at >= NOW() - INTERVAL '24 hours'
                GROUP BY DATE_TRUNC('hour', created_at AT TIME ZONE 'Asia/Ho_Chi_Minh')
                ORDER BY hour ASC
            """)
            hourly_rows = cur.fetchall()
            # Convert datetime to ISO string for JSON serialization
            metrics['hourly_requests'] = [
                {"hour": row['hour'].isoformat(), "count": row['count']}
                for row in hourly_rows
            ]
            
            return metrics
    except Exception as e:
        print(f"Error fetching metrics: {e}")
        return {}
    finally:
        conn.close()

def get_recent_logs(limit: int = 50):
    """Retrieves recent request logs."""
    conn = get_connection()
    if not conn:
        return []
        
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT id, request_id, 
                       created_at AT TIME ZONE 'Asia/Ho_Chi_Minh' as created_at, 
                       endpoint, latency_ms, landmark_name, confidence, success, user_feedback, ground_truth 
                FROM request_logs 
                ORDER BY created_at DESC 
                LIMIT %s
            """, (limit,))
            # Convert datetime to string for JSON serialization
            logs = []
            for row in cur.fetchall():
                row['created_at'] = row['created_at'].isoformat()
                logs.append(row)
            return logs
    except Exception as e:
        print(f"Error fetching logs: {e}")
        return []
    finally:
        conn.close()
