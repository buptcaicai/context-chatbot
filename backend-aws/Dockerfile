FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
   apt-get install -y --no-install-recommends \
   gcc \
   build-essential \
   && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && \
   pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY src/* .

# Expose port (if needed, e.g. for FastAPI/Flask, adjust as necessary)
EXPOSE 8000

# Default command (adjust as needed)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
