import streamlit as st
from PIL import Image
import pandas as pd
import time

st.set_page_config(page_title="Vietnam Landmark QA System", layout="wide")

# MOCKUP FUNCTIONS 
def call_app_server(image, prompt):
    """Giả lập xử lý từ App Server và Model Server"""
    time.sleep(1.5)
    return {
        "answer": f"Dựa trên hình ảnh, đây là **Nhà thờ Đức Bà Sài Gòn**. {prompt if prompt else ''}",
        "history": "Xây dựng từ năm 1877 đến 1880, đây là một tuyệt tác kiến trúc Pháp tại Việt Nam.",
        "confidence": 0.95,
        "sources": ["Wikipedia", "Cổng thông tin du lịch TP.HCM"]
    }

def get_admin_metrics():
    """Giả lập lấy dữ liệu từ Database cho Dashboard Admin"""
    return {
        "accuracy": 0.92,
        "f1_score": 0.89,
        "avg_latency": "1.2s",
        "requests": [10, 25, 45, 30, 60, 85, 70]
    }

# MAIN INTERFACE
st.sidebar.title("Điều hướng")
role = st.sidebar.radio("Chọn vai trò:", ["Người dùng (User)", "Quản trị viên (Admin)"])

if role == "Người dùng (User)":
    st.title("Khám phá Địa danh Việt Nam qua AI")
    st.caption("Hệ thống hỏi đáp đa phương thức sử dụng Agentic AI")
    
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("Tải lên hình ảnh")
        uploaded_file = st.file_uploader("Chọn ảnh địa danh/công trình...", type=["jpg", "png", "jpeg"])
        if uploaded_file:
            image = Image.open(uploaded_file)
            st.image(image, caption="Ảnh đã tải lên", use_container_width=True)

    with col2:
        st.subheader("Đặt câu hỏi")
        user_prompt = st.text_area("Bạn muốn biết gì về công trình này?", 
                                  placeholder="Ví dụ: Tòa nhà này xây dựng năm nào?")
        
        if st.button("Gửi yêu cầu"):
            if uploaded_file:
                with st.spinner("Agent đang suy luận bối cảnh..."):
                    # Call App Server
                    result = call_app_server(uploaded_file, user_prompt)
                    
                    st.success("Đã tìm thấy thông tin!")
                    st.markdown(f"### Kết quả: \n{result['answer']}")
                    st.info(f"**Lịch sử & Kiến trúc:** {result['history']}")
                    
                    st.markdown(f"**Nguồn trích dẫn:** {', '.join(result['sources'])}")
                    st.progress(result['confidence'], text=f"Độ tin cậy: {result['confidence']*100}%")
            else:
                st.warning("Vui lòng tải ảnh lên trước khi hỏi.")

elif role == "Người dùng (User)" == False or role == "Quản trị viên (Admin)":
    st.title("Admin Dashboard")
    password = st.text_input("Nhập mật mã Admin", type="password")
    
    if password == "123":
        metrics = get_admin_metrics()
        
        # Metric Row
        m1, m2, m3 = st.columns(3)
        m1.metric("Độ chính xác (Accuracy)", f"{metrics['accuracy']*100}%")
        m2.metric("F1-Score", metrics['f1_score'])
        m3.metric("Độ trễ TB (Latency)", metrics['avg_latency'])
        
        # Monitoring
        st.subheader("Lưu lượng truy vấn theo thời gian")
        chart_data = pd.DataFrame(metrics['requests'], columns=['Số lượng yêu cầu'])
        st.line_chart(chart_data)
        
        st.write("Hệ thống đang hoạt động ổn định.")
    elif password:
        st.error("Mật mã không chính xác!")