import streamlit as st
from PIL import Image
import pandas as pd
import io
import uuid
import os
import requests
from datetime import datetime

# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="Vietnam Landmark QA",
    page_icon="🏯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------- GLOBAL CSS ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

/* ---- Global ---- */
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* ---- Sidebar ---- */
[data-testid="stSidebar"] {
    background: #0D1117;
    border-right: 1px solid #21262D;
}
[data-testid="stSidebar"] * { color: #C9D1D9 !important; }
[data-testid="stSidebar"] .stButton > button {
    background: #161B22;
    border: 1px solid #30363D;
    border-radius: 8px;
    color: #C9D1D9 !important;
    width: 100%;
    transition: all 0.2s;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: #21262D;
    border-color: #58A6FF;
    color: #58A6FF !important;
}
.sidebar-title {
    font-size: 0.78rem; font-weight: 600; letter-spacing: 0.08em;
    color: #484F58 !important; text-transform: uppercase; margin-bottom: 0.8rem;
}
.conv-item {
    padding: 0.5rem 0.6rem; border-radius: 8px; cursor: pointer;
    font-size: 0.88rem; color: #8B949E !important;
    overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
    transition: background 0.15s;
}
.conv-item:hover { background: #161B22; }
.conv-item.active { background: #161B22; color: #C9D1D9 !important; }

/* ---- Topbar ---- */
.topbar {
    padding: 1.5rem 0 2.5rem 0;
    display: flex; flex-direction: column; align-items: center; text-align: center;
}
.topbar-logo {
    font-size: 3.2rem; font-weight: 900;
    background: linear-gradient(90deg, #58A6FF, #79C0FF, #A5D6FF);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    letter-spacing: -0.02em;
    margin-bottom: 0.2rem;
}
.topbar-sub { font-size: 1.1rem; color: #8B949E; font-weight: 500; }

/* ---- Greeting ---- */
.greeting-wrap {
    display: flex; flex-direction: column;
    justify-content: center; align-items: center;
    min-height: 52vh; text-align: center; padding: 2rem;
}
.greeting-emoji { font-size: 3.5rem; margin-bottom: 1rem; animation: float 3s ease-in-out infinite; }
@keyframes float {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-8px); }
}
.greeting-title {
    font-size: 2rem; font-weight: 700;
    background: linear-gradient(135deg, #58A6FF, #A5D6FF);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    margin-bottom: 0.5rem;
}
.greeting-sub { font-size: 1rem; color: #484F58; max-width: 420px; line-height: 1.6; }
.suggestion-chips { display: flex; flex-wrap: wrap; gap: 0.5rem; justify-content: center; margin-top: 1.5rem; }
.chip {
    background: #161B22; border: 1px solid #30363D; color: #8B949E;
    border-radius: 20px; padding: 0.35rem 0.9rem; font-size: 0.82rem;
    cursor: pointer; transition: all 0.2s;
}
.chip:hover { border-color: #58A6FF; color: #58A6FF; }

/* ---- Chat Messages ---- */
.stChatMessage { border-radius: 12px; margin-bottom: 0.5rem; }

/* ---- Answer card ---- */
.answer-card {
    background: #161B22; border: 1px solid #21262D; border-radius: 14px;
    padding: 1.2rem 1.4rem; margin-top: 0.3rem;
    box-shadow: 0 2px 12px rgba(0,0,0,0.3);
}
.answer-text { color: #C9D1D9; font-size: 0.97rem; line-height: 1.7; margin-bottom: 1rem; }
.info-grid { display: flex; flex-wrap: wrap; gap: 0.6rem; margin-top: 0.8rem; }
.info-chip {
    background: #0D1117; border: 1px solid #30363D; border-radius: 10px;
    padding: 0.4rem 0.85rem; font-size: 0.82rem; color: #8B949E;
    display: flex; align-items: center; gap: 0.4rem;
}
.info-chip .val { color: #C9D1D9; font-weight: 600; }
.conf-bar-wrap { margin-top: 0.9rem; }
.conf-label { font-size: 0.78rem; color: #484F58; margin-bottom: 0.3rem; }
.conf-bar-bg { background: #21262D; border-radius: 6px; height: 6px; }
.conf-bar-fill { border-radius: 6px; height: 6px; transition: width 0.6s ease; }

/* ---- Dashboard CSS (Dark) ---- */
.dash-subtitle {
    text-align: center; color: #8B949E; font-size: 1.05rem;
    margin-bottom: 2rem; font-weight: 500; letter-spacing: 0.02em;
}
.kpi-card {
    background: #161B22; border-radius: 14px; padding: 1.2rem 1.4rem;
    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    display: flex; justify-content: space-between; align-items: center;
    margin-bottom: 0.8rem; transition: transform 0.2s, box-shadow 0.2s;
    border: 1px solid #21262D;
}
.kpi-card:hover { transform: translateY(-2px); box-shadow: 0 8px 30px rgba(0,0,0,0.4); }
.kpi-card.border-cyan    { border-left: 3px solid #22D3EE; }
.kpi-card.border-emerald { border-left: 3px solid #34D399; }
.kpi-card.border-amber   { border-left: 3px solid #FBBF24; }
.kpi-card.border-rose    { border-left: 3px solid #FB7185; }
.kpi-card.border-violet  { border-left: 3px solid #A78BFA; }
.kpi-label { font-size: 0.78rem; color: #484F58; margin-bottom: 0.25rem; letter-spacing: 0.04em; text-transform: uppercase; }
.kpi-val { font-size: 1.75rem; font-weight: 700; color: #E6EDF3; }
.kpi-sub { font-size: 0.75rem; color: #484F58; margin-top: 0.15rem; }
.kpi-icon {
    width: 42px; height: 42px; border-radius: 10px;
    display: flex; align-items: center; justify-content: center; font-size: 1.2rem;
}
.icon-cyan    { background: rgba(34,211,238,0.12); }
.icon-emerald { background: rgba(52,211,153,0.12); }
.icon-amber   { background: rgba(251,191,36,0.12); }
.icon-rose    { background: rgba(251,113,133,0.12); }
.icon-violet  { background: rgba(167,139,250,0.12); }
.box-card {
    background: #161B22; border-radius: 14px; padding: 1.4rem;
    box-shadow: 0 4px 20px rgba(0,0,0,0.3); border: 1px solid #21262D;
}
.box-title { font-size: 1rem; font-weight: 600; color: #C9D1D9; margin-bottom: 1rem; }
.status-dot { width: 9px; height: 9px; border-radius: 50%; display: inline-block; margin-right: 0.5rem; }
.pill {
    background: rgba(52,211,153,0.12); color: #34D399;
    border: 1px solid rgba(52,211,153,0.25);
    padding: 0.45rem 1.1rem; border-radius: 20px; font-size: 1.15rem;
    font-weight: 600; display: inline-block; margin: 0.6rem 0;
}
.tbl { width: 100%; border-collapse: collapse; font-size: 0.88rem; }
.tbl th { text-align: left; padding: 0.55rem 0.7rem; color: #484F58;
           border-bottom: 1px solid #21262D; font-weight: 600; text-transform: uppercase; font-size: 0.75rem; letter-spacing: 0.05em; }
.tbl td { padding: 0.5rem 0.7rem; border-bottom: 1px solid #21262D; color: #8B949E; }
.tbl tr:last-child td { border-bottom: none; }
.tbl tr:hover td { background: #0D1117; color: #C9D1D9; }
.tbl .rank { color: #30363D; font-weight: 700; width: 28px; }
.footer-note {
    background: #0D1117; color: #484F58; padding: 0.65rem 1rem;
    border-radius: 8px; font-size: 0.8rem; margin-top: 1.5rem;
    border: 1px solid #21262D;
}

/* ---- Login card ---- */
.login-card {
    max-width: 380px; margin: 3rem auto;
    background: #161B22; border: 1px solid #21262D;
    border-radius: 16px; padding: 2rem;
    box-shadow: 0 8px 32px rgba(0,0,0,0.4);
}
.login-title { font-size: 1.3rem; font-weight: 700; color: #E6EDF3; margin-bottom: 0.3rem; }
.login-sub { font-size: 0.85rem; color: #484F58; margin-bottom: 1.5rem; }

/* ---- Mobile ---- */
@media (max-width: 768px) {
    [data-testid="stSidebar"] { min-width: unset; width: 75vw; }
    .main .block-container { padding-left: 1rem; padding-right: 1rem; padding-bottom: 6rem; }
    .topbar { padding: 1rem 0 2rem 0; }
    .topbar-logo { font-size: 2.2rem; }
    .greeting-title { font-size: 1.4rem; }
}
</style>
""", unsafe_allow_html=True)


# ---------- API HELPERS ----------
def call_app_server(image, prompt):
    base_url = os.environ.get("API_URL", "http://localhost:8000/process")
    data = {"prompt": prompt}
    files = None
    if image is not None:
        files = {"image": (image.name, image.getvalue(), image.type)}
    else:
        files = {"prompt": (None, prompt)}
        data = None
    try:
        response = requests.post(base_url, files=files, data=data, timeout=60)
        if response.status_code == 200:
            return response.json()
        return {"answer": f"System Error ({response.status_code})", "landmark": "Unknown", "confidence": 0}
    except Exception as e:
        return {"answer": f"Connection Error: {str(e)}", "landmark": "Unknown", "confidence": 0}

def get_admin_metrics():
    base_url = os.environ.get("API_URL", "http://localhost:8000").replace("/process", "")
    try:
        r = requests.get(base_url + "/admin/metrics", timeout=5)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None

def submit_feedback_to_backend(req_id, is_correct, ground_truth=None):
    base_url = os.environ.get("API_URL", "http://localhost:8000").replace("/process", "")
    try:
        data = {
            "request_id": req_id,
            "is_correct": is_correct,
            "actual_landmark": ground_truth
        }
        requests.post(f"{base_url}/admin/feedback", json=data, timeout=5)
    except Exception as e:
        print(f"Feedback error: {e}")


# ---------- SESSION STATE ----------
if "conversations" not in st.session_state:
    st.session_state.conversations = {}
if "current_conv_id" not in st.session_state:
    first_id = str(uuid.uuid4())
    st.session_state.conversations[first_id] = {
        "id": first_id, "title": "New chat",
        "messages": [], "created_at": datetime.now()
    }
    st.session_state.current_conv_id = first_id
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "role_mode" not in st.session_state:
    st.session_state.role_mode = "user"
if "file_uploader_key" not in st.session_state:
    st.session_state.file_uploader_key = 0


# ---------- HELPERS ----------
def get_current_conv():
    return st.session_state.conversations[st.session_state.current_conv_id]

def add_message(role, content, image_bytes=None):
    conv = get_current_conv()
    conv["messages"].append({"role": role, "content": content, "image": image_bytes, "ts": datetime.now()})
    if role == "user" and len(conv["messages"]) == 1:
        conv["title"] = content[:32] + ("..." if len(content) > 32 else "")

def new_conversation():
    nid = str(uuid.uuid4())
    st.session_state.conversations[nid] = {
        "id": nid, "title": "New chat", "messages": [], "created_at": datetime.now()
    }
    st.session_state.current_conv_id = nid
    st.session_state.file_uploader_key += 1
    st.rerun()

def delete_conversation(cid):
    if cid in st.session_state.conversations:
        del st.session_state.conversations[cid]
        if st.session_state.current_conv_id == cid:
            if st.session_state.conversations:
                st.session_state.current_conv_id = list(st.session_state.conversations.keys())[0]
            else:
                new_conversation()
        st.rerun()

def conf_color(conf):
    if conf >= 0.8: return "#34D399"
    if conf >= 0.5: return "#FBBF24"
    return "#FB7185"


# ========== SIDEBAR ==========
with st.sidebar:
    st.markdown("<div class='sidebar-title'>Vietnam Landmark QA</div>", unsafe_allow_html=True)
    if st.button("New Chat", icon=":material/add:", key="new_chat_btn", use_container_width=True):
        new_conversation()
    
    st.markdown("<div class='sidebar-title' style='margin-top:1.2rem;'>Conversations</div>", unsafe_allow_html=True)
    for cid, conv in sorted(st.session_state.conversations.items(), key=lambda x: x[1]["created_at"], reverse=True):
        c1, c2 = st.columns([8, 2])
        with c1:
            is_active = cid == st.session_state.current_conv_id
            if st.button(conv["title"], key=f"sel_{cid}", use_container_width=True, type="secondary" if is_active else "tertiary"):
                st.session_state.current_conv_id = cid
                st.rerun()
        with c2:
            if st.button("", icon=":material/delete:", key=f"del_{cid}", help="Delete conversation", use_container_width=True, type="secondary" if is_active else "tertiary"):
                delete_conversation(cid)
    
    st.markdown("---")
    st.markdown("<div class='sidebar-title'>Mode</div>", unsafe_allow_html=True)
    if st.button("User Mode", icon=":material/person:", use_container_width=True, type="primary" if st.session_state.role_mode == "user" else "secondary"):
        st.session_state.role_mode = "user"
        st.session_state.authenticated = False
        st.rerun()
    if st.button("Admin Mode", icon=":material/admin_panel_settings:", use_container_width=True, type="primary" if st.session_state.role_mode == "admin" else "secondary"):
        st.session_state.role_mode = "admin"
        st.rerun()


# ========== TOPBAR ==========
st.markdown("""
<div class="topbar">
    <div class="topbar-logo">Vietnam Landmark QA 🏯</div>
    <div class="topbar-sub">Multimodal AI — Landmark Recognition & Q&A</div>
</div>
""", unsafe_allow_html=True)


# ========== ADMIN MODE ==========
if st.session_state.role_mode == "admin":
    if not st.session_state.authenticated:
        st.markdown("<br><br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 1.2, 1])
        with col2:
            with st.form("login_form", border=True):
                st.markdown("<h3 style='text-align:center; color: #E6EDF3; margin-top:0.5rem; margin-bottom: 0;'>Admin Login</h3>", unsafe_allow_html=True)
                st.markdown("<p style='text-align:center; font-size: 0.9rem; color: #8B949E; margin-bottom: 1.5rem;'>Enter password to access the Dashboard</p>", unsafe_allow_html=True)
                password = st.text_input("Password", type="password", placeholder="Enter admin password...", label_visibility="collapsed")
                st.markdown("<br>", unsafe_allow_html=True)
                submit = st.form_submit_button("Login", type="primary", use_container_width=True)
                
                if submit:
                    if password == "123":
                        st.session_state.authenticated = True
                        st.rerun()
                    else:
                        st.error("Incorrect password!")
    else:
        metrics = get_admin_metrics()

        st.markdown("""
        <style>
        .main .block-container { background: #0D1117; }
        section[data-testid="stMainBlockContainer"] { background: #0D1117; }
        </style>
        """, unsafe_allow_html=True)

        if metrics is None:
            st.warning("Cannot connect to Backend API (http://localhost:8000). Please check if the Backend is running.")
        else:
            st.markdown("<div class='dash-subtitle'>Monitor system performance and operational status</div>", unsafe_allow_html=True)

            total_req    = metrics.get("total_requests", 0) or 0
            avg_latency  = metrics.get("avg_latency_ms", 0) or 0
            avg_conf     = metrics.get("avg_confidence", 0) or 0
            success_rate = metrics.get("success_rate_percent", 0) or 0
            feedback_acc = metrics.get("feedback_accuracy_percent", 0) or 0
            total_fb     = metrics.get("total_feedback_received", 0) or 0
            unknown_rate = metrics.get("unknown_rate_percent", 0) or 0
            top_landmarks = metrics.get("top_landmarks", []) or []
            top_failures  = metrics.get("top_failures", []) or []
            hourly_data   = metrics.get("hourly_requests", []) or []

            # ---- KPI Row ----
            k1, k2, k3, k4, k5 = st.columns(5)
            with k1:
                st.markdown(f"""<div class="kpi-card border-emerald">
                    <div><div class="kpi-label">Feedback Accuracy</div>
                    <div class="kpi-val">{feedback_acc:.1f}%</div>
                    <div class="kpi-sub">{total_fb} feedbacks</div></div>
                    <div class="kpi-icon icon-emerald">✓</div>
                </div>""", unsafe_allow_html=True)
            with k2:
                st.markdown(f"""<div class="kpi-card border-cyan">
                    <div><div class="kpi-label">Success Rate</div>
                    <div class="kpi-val">{success_rate:.1f}%</div></div>
                    <div class="kpi-icon icon-cyan">🟢</div>
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

            # ---- Line Chart ----
            st.markdown('<div class="box-card"><div class="box-title">Request Volume — Last 24h</div>', unsafe_allow_html=True)
            if hourly_data:
                chart_df = pd.DataFrame(hourly_data)
                chart_df["hour"] = pd.to_datetime(chart_df["hour"])
                chart_df = chart_df.set_index("hour")
                chart_df.columns = ["Requests"]
                st.line_chart(chart_df, color="#58A6FF")
            else:
                st.markdown("<div style='color:#484F58;text-align:center;padding:2rem;'>No data available for the last 24 hours.</div>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # ---- Status + Top Landmarks ----
            cl, cr = st.columns([1, 1.3])
            with cl:
                if success_rate >= 90:
                    dot_color, status_text = "#34D399", "System is operating normally"
                elif success_rate >= 70:
                    dot_color, status_text = "#FBBF24", "System shows signs of instability"
                else:
                    dot_color, status_text = "#FB7185", "System is experiencing critical issues"

                st.markdown(f"""<div class="box-card">
                    <div class="box-title">System Status</div>
                    <div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:1rem;">
                        <span class="status-dot" style="background:{dot_color};box-shadow:0 0 8px {dot_color};"></span>
                        <span style="color:#8B949E;font-size:0.9rem;">{status_text}</span>
                    </div>
                    <div class="pill">{success_rate:.1f}% request success</div>
                    <div style="color:#484F58;font-size:0.82rem;margin-top:0.5rem;">
                        Data is updated in real-time from Supabase.
                    </div>
                </div>""", unsafe_allow_html=True)

            with cr:
                if top_landmarks:
                    rows = "".join(
                        f"<tr><td class='rank'>{i}</td><td>{lm.get('landmark_name','N/A')}</td>"
                        f"<td style='text-align:right;color:#58A6FF;font-weight:600;'>{lm.get('count',0)}</td></tr>"
                        for i, lm in enumerate(top_landmarks, 1)
                    )
                    tbl = f"""<table class="tbl">
                        <thead><tr><th>#</th><th>Landmark</th><th style='text-align:right;'>Requests</th></tr></thead>
                        <tbody>{rows}</tbody></table>"""
                else:
                    tbl = "<div style='color:#484F58;'>No data available.</div>"
                st.markdown(f"""<div class="box-card">
                    <div class="box-title">Top Detected Landmarks</div>{tbl}</div>""", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # ---- Top Failures ----
            if top_failures:
                fail_rows = "".join(
                    f"<tr><td class='rank'>{i}</td><td>{f.get('actual_landmark','N/A')}</td>"
                    f"<td style='text-align:right;color:#FB7185;font-weight:600;'>{f.get('fail_count',0)}</td></tr>"
                    for i, f in enumerate(top_failures, 1)
                )
                st.markdown(f"""<div class="box-card">
                    <div class="box-title">Top Misidentifications (User Reported)</div>
                    <table class="tbl">
                        <thead><tr><th>#</th><th>Actual Landmark</th><th style='text-align:right;'>Fail Count</th></tr></thead>
                        <tbody>{fail_rows}</tbody>
                    </table>
                </div>""", unsafe_allow_html=True)

            st.markdown('<div class="footer-note">Monitoring Dashboard — Live data queried directly from Supabase database (UTC+7).</div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Logout"):
            st.session_state.authenticated = False
            st.rerun()


# ========== USER MODE ==========
else:
    conv = get_current_conv()
    messages = conv["messages"]

    # Chat area
    chat_container = st.container()
    with chat_container:
        if not messages:
            st.markdown("""
            <div class="greeting-wrap">
                <div class="greeting-emoji">🏯</div>
                <div class="greeting-title">Welcome!</div>
                <div class="greeting-sub">
                    I can identify Vietnamese landmarks from images and answer questions about history, culture, and tourism.
                </div>
                <div class="suggestion-chips">
                    <span class="chip">Where is Notre-Dame Cathedral?</span>
                    <span class="chip">History of Ha Long Bay</span>
                    <span class="chip">Is Golden Bridge beautiful?</span>
                    <span class="chip">What is in Hoi An?</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            for msg in messages:
                with st.chat_message(msg["role"]):
                    if msg.get("image"):
                        st.image(msg["image"], caption="Attached image", width=260)

                    if msg["role"] == "assistant" and isinstance(msg.get("_data"), dict):
                        # Rich answer card
                        d = msg["_data"]
                        answer  = d.get("answer", "")
                        lm_name = d.get("landmark", "Unknown")
                        city    = d.get("city", "")
                        country = d.get("country", "")
                        conf    = d.get("confidence", 0) or 0
                        conf_pct = int(conf * 100)
                        bar_color = conf_color(conf)

                        city_chip = f"<div class='info-chip'>📍 <span class='val'>{city}</span></div>" if city and city != "Unknown" else ""
                        country_chip = f"<div class='info-chip'>🌏 <span class='val'>{country}</span></div>" if country and country != "Unknown" else ""
                        lm_chip = f"<div class='info-chip'>🏛 <span class='val'>{lm_name}</span></div>" if lm_name and lm_name != "Unknown" else ""

                        # Display the answer using native markdown
                        st.markdown(answer)

                        # Display the metadata card (Landmark info & Confidence) below - compressed into one line
                        html_str = f'<div class="answer-card" style="margin-top: 0.8rem; padding: 1rem 1.2rem;"><div class="info-grid" style="margin-top: 0;">{lm_chip}{city_chip}{country_chip}</div><div class="conf-bar-wrap"><div class="conf-label">Confidence: {conf_pct}%</div><div class="conf-bar-bg"><div class="conf-bar-fill" style="width:{conf_pct}%;background:{bar_color};"></div></div></div></div>'
                        st.markdown(html_str, unsafe_allow_html=True)
                        
                        # --- Feedback UI ---
                        req_id = d.get("request_id")
                        if req_id and not d.get("feedback_submitted"):
                            st.markdown("<div style='margin-top: 0.5rem;'></div>", unsafe_allow_html=True)
                            fb_col1, fb_col2, fb_col3 = st.columns([1.5, 1.5, 7])
                            
                            with fb_col1:
                                if st.button("Correct", icon=":material/thumb_up:", key=f"like_{req_id}", use_container_width=True):
                                    submit_feedback_to_backend(req_id, True)
                                    msg["_data"]["feedback_submitted"] = True
                                    st.rerun()
                                    
                            with fb_col2:
                                if st.button("Incorrect", icon=":material/thumb_down:", key=f"dislike_{req_id}", use_container_width=True):
                                    st.session_state[f"show_dislike_{req_id}"] = not st.session_state.get(f"show_dislike_{req_id}", False)
                            
                            # If disliked, show input for ground truth
                            if st.session_state.get(f"show_dislike_{req_id}"):
                                with st.container(border=True):
                                    gt_input = st.text_input("What is the correct landmark?", key=f"gt_{req_id}", placeholder="e.g. Chùa Một Cột")
                                    if st.button("Submit Correction", key=f"sub_{req_id}", type="primary"):
                                        submit_feedback_to_backend(req_id, False, gt_input if gt_input.strip() else None)
                                        msg["_data"]["feedback_submitted"] = True
                                        st.session_state[f"show_dislike_{req_id}"] = False
                                        st.rerun()
                        elif d.get("feedback_submitted"):
                            st.markdown("<span style='font-size:0.85rem; color:#34D399; font-weight: 500;'>✓ Thank you for your feedback!</span>", unsafe_allow_html=True)

                    else:
                        st.markdown(msg["content"])

    # Input area
    prompt = st.chat_input("Ask a question about landmarks, architecture, history...")
    uploaded_file = st.file_uploader(
        "Upload image", type=["jpg", "jpeg", "png"],
        label_visibility="collapsed",
        key=f"uploader_{st.session_state.file_uploader_key}"
    )

    if prompt or uploaded_file:
        if uploaded_file and not prompt:
            st.warning("Please enter a question along with your image.")
        elif prompt:
            img_bytes = None
            if uploaded_file:
                pil_img = Image.open(uploaded_file)
                buf = io.BytesIO()
                pil_img.save(buf, format="PNG")
                img_bytes = buf.getvalue()

            add_message("user", prompt, img_bytes)

            with st.spinner("Analyzing..."):
                result = call_app_server(uploaded_file, prompt)

            # Store rich data for card rendering
            answer_text = result.get("answer", "No answer available.")
            msg_obj = {
                "role": "assistant",
                "content": answer_text,
                "image": None,
                "ts": datetime.now(),
                "_data": result
            }
            conv["messages"].append(msg_obj)

            st.session_state.file_uploader_key += 1
            st.rerun()