# Multimodal Question-Answering System
**Môn học:** Ứng dụng Xử lý ngôn ngữ tự nhiên trong doanh nghiệp 
**Trường:** Đại học Khoa học Tự nhiên - ĐHQG-HCM

---

##  1. Giới thiệu dự án
Dự án tập trung giải quyết bài toán nhận diện và cung cấp thông tin chuyên sâu về các địa danh, công trình kiến trúc và di sản văn hóa tại Việt Nam. Bằng cách kết hợp **Agentic AI** và **Multimodal AI**, hệ thống cho phép người dùng tương tác thông qua cả hình ảnh và ngôn ngữ tự nhiên để truy xuất dữ liệu lịch sử một cách chính xác.

---

## 2. Nhóm sinh viên thực hiện:
1. **Trần Kim Ngân**
2. **Vũ Duy Thụ**
3. **Nguyễn Duy Khánh** 
4. **Đỗ Quốc Thịnh** 
 
---

##  3. Hướng dẫn cài đặt và khởi chạy

### **Bước 1: Tạo môi trường ảo (venv)**
Mở Terminal (hoặc CMD/PowerShell) tại thư mục dự án và chạy:
```bash
python -m venv venv
```
### **Bước 2: Kích hoạt môi trường:**
- Windows:
```bash 
venv\Scripts\activate
```
- macOS/Linux:
```bash
source venv/bin/activate
```

**Bước 3:** Cài đặt các thư viện cần thiết
```bash
pip install -r requirements.txt
```

**Bước 4:** Khởi chạy ứng dụng tại terminal, gõ lệnh:
```bash
cd .\src\
streamlit run app.py
```

---

## 4. Các tính năng chính
### 4.1. Giao diện người dùng
- Tải ảnh & Truy vấn: Người dùng upload ảnh địa danh và đặt câu hỏi bằng tiếng Việt (Ví dụ: "Tòa nhà này xây dựng năm nào?").
- Xử lý đa phương thức: Agentic AI tự phân rã câu hỏi và kết hợp dữ liệu ảnh với văn bản để trả lời.
- Minh bạch thông tin: Mọi câu trả lời đều đi kèm trích dẫn nguồn (Wikipedia, Cổng du lịch) và chỉ số tin cậy.
### 4.2. Giao diện Quản trị (Admin)
- Dashboard Monitoring: Theo dõi các chỉ số kỹ thuật như Accuracy, F1-score và độ trễ (Latency).
- Quản lý hiệu suất: Giám sát lưu lượng truy cập và mức độ tương tác của người dùng.

---

## 5. Đạo đức và Trách nhiệm AI 
Dự án tuân thủ các nguyên tắc đạo đức nghiêm ngặt:
- Chống thiên kiến: Hiệu chỉnh mô hình để hoạt động chính xác trên cả phương ngữ vùng miền và các địa danh ở vùng sâu vùng xa.
- Bảo mật & Quyền riêng tư: Tích hợp bộ lọc để từ chối xử lý hình ảnh nhạy cảm hoặc khu vực cấm.
- Ngăn chặn lạm dụng: Thiết lập rào chắn để Agent từ chối các câu hỏi mang tính xuyên tạc lịch sử hoặc chính trị.

---

© 2026 Nhóm thực hiện - University of Science (VNU-HCM)