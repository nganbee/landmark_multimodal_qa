FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy frontend requirements file
COPY src/frontend/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy only the frontend source code
COPY src/frontend ./src/frontend

# Set PYTHONPATH
ENV PYTHONPATH=/app

# Expose Streamlit port
EXPOSE 8501

# Start frontend
CMD ["streamlit", "run", "src/frontend/app.py", "--server.port", "8501", "--server.address", "0.0.0.0"]
