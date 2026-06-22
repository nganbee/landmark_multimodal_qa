import streamlit as st
from PIL import Image
import pandas as pd
import time
import io
import uuid
from datetime import datetime

import requests

# ---------- PAGE CONFIG (MOBILE-FRIENDLY) ----------
st.set_page_config(
    page_title="Vietnam Landmark QA - AI Agent",
    page_icon="🏯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------- CUSTOM CSS FOR RESPONSIVE & MOBILE ----------
st.markdown("""
<style>
    /* Mobile viewport scaling */
    @viewport {
        width: device-width;
        initial-scale: 1;
    }
    /* Sidebar: make it collapsible and narrower on mobile */
    @media (max-width: 768px) {
        [data-testid="stSidebar"] {
            min-width: unset;
            width: 70vw;
        }
        .main .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
            padding-bottom: 6rem;
        }
        /* Chat input wrapper: full width, better positioning */
        .chat-input-wrapper {
            left: 1rem !important;
            right: 1rem !important;
            bottom: 0.8rem !important;
            border-radius: 2rem;
            padding: 0.3rem 0.8rem;
        }
        .greeting-box {
            min-height: 40vh;
            font-size: 1.1rem;
            padding: 0 1rem;
        }
    }
    /* Desktop adjustments */
    [data-testid="stSidebar"] {
        background-color: var(--secondary-background-color);
        border-right: 1px solid var(--border-color);
        padding-top: 2rem;
    }
    .conv-title {
        font-size: 0.9rem;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }
    /* Chat input area - integrated, bigger, rounder */
    .chat-input-wrapper {
        position: fixed;
        bottom: 2rem;
        left: 25%;
        right: 2rem;
        background: var(--background-color);
        border: 1px solid var(--border-color);
        border-radius: 2.5rem;
        padding: 0.5rem 1rem;
        backdrop-filter: blur(10px);
        z-index: 100;
        display: flex;
        align-items: center;
        gap: 0.75rem;
        box-shadow: 0 0.2rem 0.5rem rgba(0,0,0,0.05);
    }
    .chat-input-wrapper > div:first-child {
        flex-grow: 1;
    }
    .stChatInput > div {
        border: none;
        box-shadow: none;
        padding: 0.75rem 0.5rem;
        font-size: 1rem;
    }
    .stFileUploader button {
        border-radius: 2rem;
        padding: 0.4rem 1rem;
    }
    /* Greeting box - larger, no icon, closer to input */
    .greeting-box {
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 55vh;
        text-align: center;
        font-size: 1.6rem;
        font-weight: bold;
        color: var(--text-color);
        opacity: 0.85;
        margin-bottom: 1rem;
        line-height: 1.4;
        padding: 0 2rem;
    }
    /* Remove extra padding from main container to bring greeting closer */
    .main .block-container {
        padding-bottom: 7rem;
    }
    /* Popover styling */
    div[data-testid="stPopover"] > div {
        background-color: var(--background-color);
        border: 1px solid var(--border-color);
    }
</style>
""", unsafe_allow_html=True)

# ---------- MOCK AI FUNCTIONS (Vietnamese output) ----------
def call_app_server(image, prompt, history_context=""):
    """Mock processing from App Server - replace with real model later."""
    # time.sleep(1.2)
    # landmark_name = "Nhà thờ Đức Bà Sài Gòn"
    # history_info = "Khởi công năm 1877, hoàn thành năm 1880, kiến trúc Gothic Roman đặc trưng."
    # if "Hà Nội" in prompt or "chùa" in prompt:
    #     landmark_name = "Chùa Một Cột"
    #     history_info = "Xây dựng năm 1049 dưới thời vua Lý Thái Tông, biểu tượng của thủ đô Hà Nội."
    # elif "Huế" in prompt or "cung đình" in prompt:
    #     landmark_name = "Đại Nội Huế"
    #     history_info = "Kinh đô nhà Nguyễn từ 1802 đến 1945, di sản văn hóa thế giới UNESCO."
    # return {
    #     "answer": f"🏛️ **{landmark_name}**\n\n{history_info}\n\n{('Trả lời: ' + prompt) if prompt else ''}",
    #     "history": history_info,
    #     "confidence": 0.92,
    #     "sources": ["Wikipedia", "Cục Di sản Văn hóa", "Vietnam Travel"]
    # }
    
    """Gửi yêu cầu thực tế tới Backend FastAPI."""
    # URL của Backend khi chạy local
    import os
    url = os.environ.get("API_URL", "http://localhost:8000/process")
    
    # Chuẩn bị dữ liệu gửi đi (Multipart Form-Data)
    data = {
        "prompt": prompt
    }

    files = None

    if image is not None:
        files = {
            "image": (
                image.name,
                image.getvalue(),
                image.type
            )
        }
    else:
        # Force multipart/form-data so FastAPI doesn't throw 422 Unprocessable Entity
        files = {
            "prompt": (None, prompt)
        }
        data = None

    try:
        # Gửi request POST tới Backend
        response = requests.post(url, files=files, data=data)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {
            "answer": "System Error: Cannot get answer from Backend",
            "landmark": "Unknown",
            "weather": "N/A",
            "confidence": 0
        }
    except Exception as e:
        return {
            "answer": f"Connection Error: {str(e)}",
            "weather": "N/A",
            "confidence": 0
        }

def get_admin_metrics():
    """Fetch real database metrics from Backend API."""
    import os
    base_url = os.environ.get("API_URL", "http://localhost:8000")
    # Remove /process suffix if present
    base_url = base_url.replace("/process", "")
    url = base_url + "/admin/metrics"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass
    # Fallback if backend is down
    return None

# ---------- SESSION STATE ----------
if "conversations" not in st.session_state:
    st.session_state.conversations = {}
if "current_conv_id" not in st.session_state:
    first_id = str(uuid.uuid4())
    st.session_state.conversations[first_id] = {
        "id": first_id,
        "title": "New conversation",
        "messages": [],
        "created_at": datetime.now()
    }
    st.session_state.current_conv_id = first_id
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "role_mode" not in st.session_state:
    st.session_state.role_mode = "user"
if "file_uploader_key" not in st.session_state:
    st.session_state.file_uploader_key = 0

# ---------- HELPER FUNCTIONS ----------
def get_current_conversation():
    return st.session_state.conversations[st.session_state.current_conv_id]

def add_message_to_current(role, content, image_bytes=None):
    conv = get_current_conversation()
    conv["messages"].append({
        "role": role,
        "content": content,
        "image": image_bytes,
        "timestamp": datetime.now()
    })
    if role == "user" and len(conv["messages"]) == 1:
        conv["title"] = content[:30] + ("..." if len(content) > 30 else "")

def create_new_conversation():
    new_id = str(uuid.uuid4())
    st.session_state.conversations[new_id] = {
        "id": new_id,
        "title": "➕ New conversation",
        "messages": [],
        "created_at": datetime.now()
    }
    st.session_state.current_conv_id = new_id
    st.session_state.file_uploader_key += 1
    st.rerun()

def delete_conversation(conv_id):
    if conv_id in st.session_state.conversations:
        del st.session_state.conversations[conv_id]
        if st.session_state.current_conv_id == conv_id:
            if st.session_state.conversations:
                st.session_state.current_conv_id = list(st.session_state.conversations.keys())[0]
            else:
                create_new_conversation()
        st.rerun()

# ---------- TOP BAR (ENGLISH TITLES, VIETNAMESE CAPTION) ----------
col_title, col_role = st.columns([6, 1])
with col_title:
    st.title("Vietnam Landmark Multimodal QA")
    st.caption("Intelligent Multimodal Q&A - Supporting Vietnam's Tourism and Culture")
with col_role:
    with st.popover("⚙️"):
        if st.button("User Mode", width="stretch"):
            st.session_state.role_mode = "user"
            st.session_state.authenticated = False
            st.rerun()
        if st.button("Admin Mode", width="stretch"):
            st.session_state.role_mode = "admin"
            st.rerun()

# ========== SIDEBAR (ENGLISH TITLE, VIETNAMESE BUTTONS) ==========
with st.sidebar:
    st.markdown("## Chat History")
    # Remove icon from New chat button as requested
    if st.button("New Chat", width="stretch"):
        create_new_conversation()
    st.markdown("---")
    for conv_id, conv in sorted(st.session_state.conversations.items(), key=lambda x: x[1]["created_at"], reverse=True):
        col1, col2 = st.columns([5, 1])
        with col1:
            if conv_id == st.session_state.current_conv_id:
                st.markdown(f"{conv['title']}")
            else:
                st.markdown(f"<div class='conv-title'>{conv['title']}</div>", unsafe_allow_html=True)
        with col2:
            with st.popover("⋮"):
                if st.button("Delete", key=f"del_{conv_id}", width="stretch"):
                    delete_conversation(conv_id)

# ========== ADMIN MODE ==========
if st.session_state.role_mode == "admin":
    st.markdown("<h2 style='color:#F1F5F9;'>Admin Dashboard</h2>", unsafe_allow_html=True)
    if not st.session_state.authenticated:
        password = st.text_input("Password", type="password")
        if st.button("Confirm"):
            if password == "123":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Wrong password!")
    else:
        metrics = get_admin_metrics()
        
        # ---- Dashboard CSS (Dark Theme) ----
        st.markdown("""
        <style>
        /* Force dark background on the main area */
        .main .block-container { background: #0B0F19; }
        section[data-testid="stMainBlockContainer"] { background: #0B0F19; }
        
        .dash-subtitle {
            text-align: center; color: #94A3B8; font-size: 1.15rem;
            margin-bottom: 2rem; font-weight: 500; letter-spacing: 0.02em;
        }
        .kpi-card {
            background: #111827; border-radius: 16px; padding: 1.3rem 1.5rem;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
            display: flex; justify-content: space-between; align-items: center;
            margin-bottom: 0.8rem; transition: transform 0.2s, box-shadow 0.2s;
        }
        .kpi-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 30px rgba(0,0,0,0.4);
        }
        /* Colored left-border accents */
        .kpi-card.border-cyan    { border-left: 4px solid #22D3EE; }
        .kpi-card.border-emerald { border-left: 4px solid #34D399; }
        .kpi-card.border-amber   { border-left: 4px solid #FBBF24; }
        .kpi-card.border-rose    { border-left: 4px solid #FB7185; }
        .kpi-card.border-violet  { border-left: 4px solid #A78BFA; }
        .kpi-card.border-sky     { border-left: 4px solid #38BDF8; }
        .kpi-card.border-orange  { border-left: 4px solid #FB923C; }
        
        .kpi-label { font-size: 0.85rem; color: #64748B; margin-bottom: 0.3rem; letter-spacing: 0.03em; }
        .kpi-val { font-size: 1.8rem; font-weight: 700; color: #F1F5F9; }
        .kpi-icon {
            width: 44px; height: 44px; border-radius: 12px;
            display: flex; align-items: center; justify-content: center;
            font-size: 1.3rem;
        }
        .icon-cyan    { background: rgba(34,211,238,0.15); color: #22D3EE; }
        .icon-emerald { background: rgba(52,211,153,0.15); color: #34D399; }
        .icon-amber   { background: rgba(251,191,36,0.15); color: #FBBF24; }
        .icon-rose    { background: rgba(251,113,133,0.15); color: #FB7185; }
        .icon-violet  { background: rgba(167,139,250,0.15); color: #A78BFA; }
        .icon-sky     { background: rgba(56,189,248,0.15); color: #38BDF8; }
        .icon-orange  { background: rgba(251,146,60,0.15); color: #FB923C; }
        
        .box-card {
            background: #111827; border-radius: 16px; padding: 1.5rem;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3); border: 1px solid #1E293B;
        }
        .box-title {
            font-size: 1.1rem; font-weight: 600; color: #E2E8F0; margin-bottom: 1rem;
        }
        .status-dot {
            width: 10px; height: 10px; border-radius: 50%;
            display: inline-block; margin-right: 0.5rem;
            box-shadow: 0 0 8px currentColor;
        }
        .pill {
            background: rgba(16,185,129,0.15); color: #34D399; border: 1px solid rgba(52,211,153,0.3);
            padding: 0.5rem 1.2rem; border-radius: 20px; font-size: 1.25rem;
            font-weight: 600; display: inline-block; margin: 0.8rem 0;
        }
        .tbl { width: 100%; border-collapse: collapse; font-size: 0.9rem; }
        .tbl th { text-align: left; padding: 0.6rem 0.8rem; color: #64748B;
                   border-bottom: 2px solid #1E293B; font-weight: 600; }
        .tbl td { padding: 0.55rem 0.8rem; border-bottom: 1px solid #1E293B; color: #CBD5E1; }
        .tbl tr:hover td { background: #1E293B; }
        .footer-note {
            background: #111827; color: #64748B; padding: 0.7rem 1rem;
            border-radius: 8px; font-size: 0.85rem; margin-top: 1.5rem;
            border: 1px solid #1E293B;
        }
        </style>
        """, unsafe_allow_html=True)
        
        if metrics is None:
            st.warning("⚠️ Không thể kết nối tới Backend API. Hãy đảm bảo Backend đang chạy tại http://localhost:8000")
        else:
            st.markdown("<div class='dash-subtitle'>Theo dõi hiệu suất và trạng thái vận hành của hệ thống</div>", unsafe_allow_html=True)
            
            # Extract values safely
            total_req = metrics.get("total_requests", 0) or 0
            avg_latency = metrics.get("avg_latency_ms", 0) or 0
            avg_conf = metrics.get("avg_confidence", 0) or 0
            success_rate = metrics.get("success_rate_percent", 0) or 0
            feedback_acc = metrics.get("feedback_accuracy_percent", 0) or 0
            total_fb = metrics.get("total_feedback_received", 0) or 0
            unknown_rate = metrics.get("unknown_rate_percent", 0) or 0
            top_landmarks = metrics.get("top_landmarks", []) or []
            top_failures = metrics.get("top_failures", []) or []
            hourly_data = metrics.get("hourly_requests", []) or []

            # ---- Row 1: 5 KPI Cards ----
            k1, k2, k3, k4, k5 = st.columns(5)
            with k1:
                st.markdown(f"""<div class="kpi-card border-emerald">
                    <div><div class="kpi-label">Feedback Accuracy</div>
                    <div class="kpi-val">{feedback_acc:.1f}%</div>
                    <div class="kpi-label" style="margin-top:0.2rem;">({total_fb} feedbacks)</div></div>
                    <div class="kpi-icon icon-emerald">✓</div>
                </div>""", unsafe_allow_html=True)
            with k2:
                st.markdown(f"""<div class="kpi-card border-emerald">
                    <div><div class="kpi-label">Success Rate</div>
                    <div class="kpi-val">{success_rate:.1f}%</div></div>
                    <div class="kpi-icon icon-emerald">🟢</div>
                </div>""", unsafe_allow_html=True)
            with k3:
                st.markdown(f"""<div class="kpi-card border-amber">
                    <div><div class="kpi-label">Avg Latency</div>
                    <div class="kpi-val">{avg_latency/1000:.2f}s</div></div>
                    <div class="kpi-icon icon-amber">⏱</div>
                </div>""", unsafe_allow_html=True)
            with k4:
                st.markdown(f"""<div class="kpi-card border-violet">
                    <div><div class="kpi-label">Avg Confidence</div>
                    <div class="kpi-val">{avg_conf*100:.1f}%</div></div>
                    <div class="kpi-icon icon-violet">🎯</div>
                </div>""", unsafe_allow_html=True)
            with k5:
                st.markdown(f"""<div class="kpi-card border-rose">
                    <div><div class="kpi-label">Unknown Rate</div>
                    <div class="kpi-val">{unknown_rate:.1f}%</div></div>
                    <div class="kpi-icon icon-rose">❓</div>
                </div>""", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # ---- Request Volume Over Time (Line Chart) ----
            st.markdown('<div class="box-card"><div class="box-title">📈 Request Volume Over Time (Last 24h)</div>', unsafe_allow_html=True)
            if hourly_data:
                from datetime import datetime as dt
                chart_df = pd.DataFrame(hourly_data)
                chart_df["hour"] = pd.to_datetime(chart_df["hour"])
                chart_df = chart_df.set_index("hour")
                chart_df.columns = ["Requests"]
                st.line_chart(chart_df, color="#22D3EE")
            else:
                st.markdown("<div style='color:#64748B;text-align:center;padding:2rem;'>Chưa có dữ liệu request trong 24 giờ qua.</div>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # ---- Row 3: System Status + Top Landmarks ----
            col_left, col_right = st.columns([1, 1.2])
            with col_left:
                # Determine status color
                if success_rate >= 90:
                    dot_color, status_text = "#10B981", "Hệ thống đang hoạt động bình thường"
                elif success_rate >= 70:
                    dot_color, status_text = "#F59E0B", "Hệ thống đang có dấu hiệu bất thường"
                else:
                    dot_color, status_text = "#EF4444", "Hệ thống đang gặp sự cố nghiêm trọng"
                
                st.markdown(f"""<div class="box-card">
                    <div class="box-title">System Status</div>
                    <div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:1rem;">
                        <span class="status-dot" style="background:{dot_color};"></span>
                        <span style="color:#64748B;font-size:1rem;">{status_text}</span>
                    </div>
                    <div class="pill">{success_rate:.1f}% request thành công</div>
                    <div style="color:#94A3B8;font-size:0.88rem;margin-top:0.5rem;">
                        Dashboard hỗ trợ quan sát nhanh các chỉ số chính.
                    </div>
                </div>""", unsafe_allow_html=True)
            
            with col_right:
                landmarks_html = ""
                if top_landmarks:
                    rows = ""
                    for i, lm in enumerate(top_landmarks, 1):
                        name = lm.get("landmark_name", "N/A")
                        count = lm.get("count", 0)
                        rows += f"<tr><td>{i}</td><td>{name}</td><td style='text-align:right;'>{count}</td></tr>"
                    landmarks_html = f"""<table class="tbl">
                        <thead><tr><th>#</th><th>Landmark</th><th style='text-align:right;'>Requests</th></tr></thead>
                        <tbody>{rows}</tbody>
                    </table>"""
                else:
                    landmarks_html = "<div style='color:#94A3B8;font-size:0.9rem;'>Chưa có dữ liệu landmark.</div>"
                
                st.markdown(f"""<div class="box-card">
                    <div class="box-title">🏛 Top Detected Landmarks</div>
                    {landmarks_html}
                </div>""", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # ---- Row 4: Top Failures ----
            if top_failures:
                fail_rows = ""
                for i, f in enumerate(top_failures, 1):
                    name = f.get("actual_landmark", "N/A")
                    count = f.get("fail_count", 0)
                    fail_rows += f"<tr><td>{i}</td><td>{name}</td><td style='text-align:right;'>{count}</td></tr>"
                
                st.markdown(f"""<div class="box-card">
                    <div class="box-title">⚠️ Top Failures (User-reported Misidentifications)</div>
                    <table class="tbl">
                        <thead><tr><th>#</th><th>Actual Landmark (Ground Truth)</th><th style='text-align:right;'>Fail Count</th></tr></thead>
                        <tbody>{fail_rows}</tbody>
                    </table>
                </div>""", unsafe_allow_html=True)
            
            st.markdown('<div class="footer-note">Monitoring Dashboard — Dữ liệu được truy vấn trực tiếp từ database Supabase theo thời gian thực.</div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Logout"):
            st.session_state.authenticated = False
            st.rerun()

# ========== USER MODE ==========
else:
    conversation = get_current_conversation()
    messages = conversation["messages"]
    
    # Display chat messages
    chat_container = st.container()
    with chat_container:
        if len(messages) == 0:
            # Greeting: larger, no icon, closer to chat input due to reduced padding
            st.markdown(
                '<div class="greeting-box">'
                '<p><strong>Hello</strong>, what landmark or building would you like to explore today?</p>'
                '</div>',
                unsafe_allow_html=True
            )
        else:
            for msg in messages:
                with st.chat_message(msg["role"]):
                    if msg.get("image"):
                        st.image(msg["image"], caption="Attached image", width=250)
                    st.markdown(msg["content"])
    
    # Integrated chat input + file upload (supports camera on mobile)
    with st.container():
        st.markdown('<div class="chat-input-wrapper">', unsafe_allow_html=True)
        prompt = st.chat_input("Ask a question about landmarks, historical sites...")
        # File uploader that also allows taking a photo directly from camera on mobile
        uploaded_file = st.file_uploader(
            "📷", type=["jpg", "jpeg", "png"],
            label_visibility="collapsed",
            key=f"uploader_{st.session_state.file_uploader_key}",
            accept_multiple_files=False
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Handle submission
    if prompt or uploaded_file:
        if uploaded_file and not prompt:
            st.warning("Please enter a question with an image.")
        elif prompt:
            image_bytes = None
            if uploaded_file:
                image = Image.open(uploaded_file)
                img_byte_arr = io.BytesIO()
                image.save(img_byte_arr, format='PNG')
                image_bytes = img_byte_arr.getvalue()
            
            add_message_to_current("user", prompt, image_bytes)
            
            with st.spinner("🧠 Thinking..."):
                result = call_app_server(uploaded_file, prompt)
                assistant_reply = f"""
{result.get('answer', 'No answer available')}

---

🏛 Landmark:
{result.get('landmark', 'Unknown')}

📍 City:
{result.get('city', 'Unknown')}

🌎 Country:
{result.get('country', 'Unknown')}

🎯 Confidence:
{result.get('confidence', 0)*100:.0f}%
"""
            add_message_to_current("assistant", assistant_reply)
            
            st.session_state.file_uploader_key += 1
            st.rerun()