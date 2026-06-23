FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements file
COPY src/backend/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project code so imports like src.backend work
COPY src/backend ./src/backend

# Set PYTHONPATH so absolute imports work (like src.backend.main)
ENV PYTHONPATH=/app

# Expose port
EXPOSE 8000

# Start backend
CMD ["uvicorn", "src.backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
