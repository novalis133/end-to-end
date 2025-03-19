# Use NVIDIA CUDA base image for GPU support
FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04

# Create non-root user for security
RUN groupadd -r inferencer && useradd -r -g inferencer inferencer

# Set working directory
WORKDIR /app

# Install Python and system dependencies
RUN apt-get update && apt-get install -y \
    python3.9 \
    python3-pip \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Create directories
RUN mkdir /security /models && \
    chown inferencer:inferencer /security /models

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy source code
COPY inference/src/ ./src/

# Set ownership
RUN chown -R inferencer:inferencer /app

# Switch to non-root user
USER inferencer

# Environment variables
ENV PYTHONPATH=/app
ENV NVIDIA_VISIBLE_DEVICES=all

# Run the inference worker
CMD ["python3", "src/inference.py"]