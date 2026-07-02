# Multimodal Question-Answering System

**Môn học:** Ứng dụng Xử lý ngôn ngữ tự nhiên trong doanh nghiệp
**Trường:** Đại học Khoa học Tự nhiên - ĐHQG-HCM

---

## 1. Giới thiệu dự án

Dự án tập trung giải quyết bài toán nhận diện và cung cấp thông tin chuyên sâu về các địa danh, công trình kiến trúc và di sản văn hóa tại Việt Nam. Bằng cách kết hợp **Agentic AI** và **Multimodal AI**, hệ thống cho phép người dùng tương tác thông qua cả hình ảnh và ngôn ngữ tự nhiên để truy xuất dữ liệu lịch sử một cách chính xác.

---

## 2. Nhóm sinh viên thực hiện:

1. **Trần Kim Ngân**
2. **Vũ Duy Thụ**
3. **Nguyễn Duy Khánh**
4. **Đỗ Quốc Thịnh**

---

## 3. Cài đặt môi trường (Environment Setup)

### Yêu cầu tiên quyết
- Cài đặt [Docker Desktop](https://www.docker.com/products/docker-desktop/) (Khuyên dùng) hoặc Python 3.10+.
- Khóa API của Groq, OpenWeather (có thể đăng ký miễn phí).

### Bước 1: Thiết lập biến môi trường
Tạo file `.env` ở thư mục gốc của dự án (có thể copy từ file `.env.example`) và điền các khóa API của bạn:
```ini
DEVICE=cpu  # hoặc cuda nếu dùng GPU
HF_TOKEN=your_huggingface_token
HF_HOME=./hf_cache
BASE_MODEL=Qwen/Qwen2.5-VL-3B-Instruct
LORA_PATH=imbee510/qwen2-5-vl-landmark-lora
OPENWEATHER_API_KEY=your_openweather_key
GROQ_API_KEY=your_groq_key
SUPABASE_URL=your_supabase_postgres_url
```

### Bước 2: Khởi chạy hệ thống

Bạn có thể chọn **1 trong 2 cách** sau để khởi chạy dự án:

#### Cách 1: Chạy bằng Docker
Hệ thống đã được đóng gói hoàn chỉnh bằng Docker. Tại thư mục gốc của dự án, mở Terminal và chạy lệnh sau:
```bash
docker-compose up --build -d
```
*(Lệnh này sẽ tự động cài đặt cả Backend (FastAPI) và Frontend (Streamlit). Quá trình tải các mô hình AI có thể mất 5-10 phút trong lần chạy đầu tiên).*

#### Cách 2: Chạy thủ công bằng Python (Venv)
Nếu không dùng Docker, bạn có thể cài đặt và chạy nội bộ theo các bước sau:

**1. Khởi tạo và kích hoạt môi trường ảo**
- Tạo môi trường:
  ```bash
  python -m venv venv
  ```
- Kích hoạt môi trường:
  - Trên Windows:
    ```bash
    venv\Scripts\activate
    ```
  - Trên macOS/Linux:
    ```bash
    source venv/bin/activate
    ```

**2. Cài đặt thư viện cần thiết**
```bash
pip install -r src/backend/requirements.txt
pip install -r src/frontend/requirements.txt
```

**3. Khởi chạy máy chủ**
Lưu ý: Bạn cần mở **2 cửa sổ Terminal khác nhau** (đảm bảo cả 2 đều đã kích hoạt `venv`):
- Terminal 1 (Chạy Backend):
  ```bash
  uvicorn src.backend.main:app --port 8000
  ```
- Terminal 2 (Chạy Frontend):
  ```bash
  streamlit run src/frontend/app.py
  ```

---

## 4. Huấn luyện mô hình

Quá trình tinh chỉnh (Fine-tuning) mô hình nhận diện địa danh bằng kỹ thuật LoRA (trên nền Qwen2.5-VL) được thực hiện độc lập với ứng dụng chính. 

- **Dữ liệu & Notebook:** Toàn bộ mã nguồn để xử lý dữ liệu và huấn luyện được đặt tại `src/modeling/landmark-qwen2-5-vl-finetune.ipynb`.
- **Cách chạy:** 
  1. Mở file notebook `landmark-qwen2-5-vl-finetune.ipynb` bằng Kaggle.
  2. Chuẩn bị tập dữ liệu ảnh các địa danh.
  3. Chạy lần lượt các cell trong notebook để tiền xử lý, cấu hình tham số LoRA và tiến hành training. Trọng số sau khi train (LoRA adapter) sẽ được đẩy lên HuggingFace hoặc lưu ở thư mục cục bộ và cấu hình vào file `.env` thông qua biến `LORA_PATH`.

---

## 5. Cách chạy dự đoán / suy luận

Sau khi hệ thống (Frontend và Backend) đã chạy thành công theo hướng dẫn ở phần Cài đặt, bạn có thể thực hiện dự đoán (inference):

1. Mở trình duyệt và truy cập: [http://localhost:8501](http://localhost:8501)
2. Chọn "Upload image" để tải lên bức ảnh về một địa danh tại Việt Nam.
3. Gõ câu hỏi của bạn (ví dụ: *"Where is this and tell me more about it?"*).
4. Bấm Gửi. Backend sẽ tự động phân tích ảnh và trả về kết quả ngay trên màn hình chat.

---

## 6. Ghi log và Theo dõi

### Ghi log hệ thống và người dùng
1. **Lưu trữ tự động:** Mọi request đi qua API `/process` (bao gồm hình ảnh gửi lên, độ trễ/latency, độ tin cậy/confidence, và kết quả suy luận) đều được tự động lưu log vào cơ sở dữ liệu **Supabase PostgreSQL**.
2. **Dashboard Quản trị:** 
   - Truy cập giao diện Streamlit tại `http://localhost:8501`.
   - Bấm vào mục **Admin Mode** trên thanh Sidebar, nhập mật khẩu admin.
   - Tại đây, hệ thống hiển thị một **Dashboard** tổng quan với các chỉ số KPI theo thời gian thực (Real-time tracking):
     - *Accuracy (Tỷ lệ dự đoán đúng qua Feedback).*
     - *Average Latency (Độ trễ trung bình của mô hình).*
     - *Success Rate (Tỷ lệ xử lý thành công).*
     - *Bảng xếp hạng các địa danh được truy vấn nhiều nhất và dễ bị nhận diện sai nhất.*

---

## 7. Đạo đức và Trách nhiệm AI

Dự án tuân thủ các nguyên tắc đạo đức nghiêm ngặt:

- **Chống thiên kiến:** Hiệu chỉnh mô hình để hoạt động chính xác trên cả phương ngữ vùng miền và các địa danh ở vùng sâu vùng xa.
- **Bảo mật & Quyền riêng tư:** Tích hợp bộ lọc để từ chối xử lý hình ảnh nhạy cảm hoặc khu vực cấm.
- **Ngăn chặn lạm dụng:** Thiết lập rào chắn để Agent từ chối các câu hỏi mang tính xuyên tạc lịch sử hoặc chính trị.

---

© 2026 Nhóm thực hiện - University of Science (VNU-HCM)
