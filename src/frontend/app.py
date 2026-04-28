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
    url = "http://localhost:8000/process"
    
    # Chuẩn bị dữ liệu gửi đi (Multipart Form-Data)
    files = {"image": (image.name, image.getvalue(), image.type)}
    data = {"prompt": prompt}

    try:
        # Gửi request POST tới Backend
        response = requests.post(url, files=files, data=data)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {
                "answer": "System Error: Can not get answer from Backend",
                "landmark": "Không xác định",
                "weather": "N/A",
                "confidence": 0
            }
    except Exception as e:
        return {
            "answer": f"Error Connection: {str(e)}",
            "landmark": "N/A",
            "weather": "N/A",
            "confidence": 0
        }

def get_admin_metrics():
    """Mock database metrics for admin dashboard."""
    return {
        "accuracy": 0.94,
        "f1_score": 0.91,
        "avg_latency": "1.05s",
        "requests": [12, 28, 42, 38, 55, 72, 68, 85, 90, 78]
    }

# ---------- SESSION STATE ----------
if "conversations" not in st.session_state:
    st.session_state.conversations = {}
if "current_conv_id" not in st.session_state:
    first_id = str(uuid.uuid4())
    st.session_state.conversations[first_id] = {
        "id": first_id,
        "title": "Hội thoại mới",
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
        "title": "➕ Hội thoại mới",
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
    st.caption("Hỏi đáp đa phương thức thông minh - Hỗ trợ du lịch và văn hóa Việt Nam")
with col_role:
    with st.popover("⚙️"):
        if st.button("User mode", width="stretch"):
            st.session_state.role_mode = "user"
            st.session_state.authenticated = False
            st.rerun()
        if st.button("Admin mode", width="stretch"):
            st.session_state.role_mode = "admin"
            st.rerun()

# ========== SIDEBAR (ENGLISH TITLE, VIETNAMESE BUTTONS) ==========
with st.sidebar:
    st.markdown("## Chat history")
    # Remove icon from New chat button as requested
    if st.button("New chat", width="stretch"):
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
                if st.button("Xóa", key=f"del_{conv_id}", width="stretch"):
                    delete_conversation(conv_id)

# ========== ADMIN MODE ==========
if st.session_state.role_mode == "admin":
    st.markdown("## Admin Dashboard")
    if not st.session_state.authenticated:
        password = st.text_input("Mật khẩu quản trị", type="password")
        if st.button("Xác nhận"):
            if password == "123":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Sai mật khẩu!")
    else:
        metrics = get_admin_metrics()
        col1, col2, col3 = st.columns(3)
        col1.metric("Độ chính xác", f"{metrics['accuracy']*100:.1f}%")
        col2.metric("F1-Score", f"{metrics['f1_score']:.2f}")
        col3.metric("Độ trễ trung bình", metrics['avg_latency'])
        
        st.subheader("Lượng truy vấn theo thời gian")
        chart_data = pd.DataFrame(metrics['requests'], columns=["Số lượng"])
        st.line_chart(chart_data)
        st.info("Hệ thống đang hoạt động ổn định, 98.7% yêu cầu thành công.")
        if st.button("Đăng xuất"):
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
                '<p><strong>Chào bạn</strong>, hôm nay bạn muốn khám phá địa điểm hay công trình nào?</p>'
                '</div>',
                unsafe_allow_html=True
            )
        else:
            for msg in messages:
                with st.chat_message(msg["role"]):
                    if msg.get("image"):
                        st.image(msg["image"], caption="Ảnh đính kèm", width=250)
                    st.markdown(msg["content"])
    
    # Integrated chat input + file upload (supports camera on mobile)
    with st.container():
        st.markdown('<div class="chat-input-wrapper">', unsafe_allow_html=True)
        prompt = st.chat_input("Nhập câu hỏi về địa danh, công trình lịch sử...")
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
            st.warning("Vui lòng nhập câu hỏi kèm theo ảnh.")
        elif prompt:
            image_bytes = None
            if uploaded_file:
                image = Image.open(uploaded_file)
                img_byte_arr = io.BytesIO()
                image.save(img_byte_arr, format='PNG')
                image_bytes = img_byte_arr.getvalue()
            
            add_message_to_current("user", prompt, image_bytes)
            
            with st.spinner("🧠 Agent đang phân tích ảnh và suy luận..."):
                result = call_app_server(uploaded_file, prompt)
                assistant_reply = f"""
**Địa danh:** {result.get('landmark', 'N/A')}
**Thời tiết:** {result.get('weather', 'N/A')}

---
{result.get('answer', 'Không có câu trả lời.')}

---
**Độ tin cậy:** {result.get('confidence', 0)*100:.0f}%
"""
            add_message_to_current("assistant", assistant_reply)
            
            st.session_state.file_uploader_key += 1
            st.rerun()