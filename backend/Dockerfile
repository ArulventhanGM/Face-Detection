# Use Python 3.9 slim image for better compatibility
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies for dlib and opencv
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    libopenblas-dev \
    liblapack-dev \
    libx11-dev \
    libgtk-3-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel
RUN pip install --no-cache-dir --timeout 600 numpy pillow
RUN pip install --no-cache-dir --timeout 600 flask flask-cors werkzeug python-multipart
RUN pip install --no-cache-dir --timeout 900 dlib
RUN pip install --no-cache-dir --timeout 600 face-recognition opencv-python-headless

# Copy application code
COPY . .

# Create uploads directory
RUN mkdir -p uploads/known_faces uploads/test_images

# Initialize database
RUN python models.py

# Expose port
EXPOSE 5000

# Run the application
CMD ["python", "app.py"]
