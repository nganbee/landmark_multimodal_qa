## Streamlit demo

- **Bước 1:** Chuẩn bị môi trường Python
    - Cài đặt Python phiên bản 3.8 trở lên. Nếu chưa có, hãy tải tại [Python](python.org)
    - Nên sử dụng môi trường ảo để quản lý thư viện dễ dàng hơn
    - Mở Terminal, hoặc Command Prompt/PowerShell.Tạo môi trường ảo ```bash
        python -m venv venv
    - Kích hoạt môi trường:
    ```bash
#### Windows: 
    venv\Scripts\activate
#### macOS/Linux: 
    source venv/bin/activate

- **Bước 2:** Cài đặt các thư viện cần thiết
```bash
    pip install streamlit pillow pandas

- **Bước 3:** Khởi chạy ứng dụng tại terminal, gõ lệnh:
```bash
    cd .\src\
    streamlit run app.py