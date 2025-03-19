# Use Python slim image for smaller footprint
FROM python:3.9-slim

# Create non-root user for security
RUN groupadd -r preprocessor && useradd -r -g preprocessor preprocessor

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create security directory
RUN mkdir /security && chown preprocessor:preprocessor /security

# Copy source code
COPY preprocess/src/ ./src/

# Set ownership
RUN chown -R preprocessor:preprocessor /app

# Switch to non-root user
USER preprocessor

# Environment variables
ENV PYTHONPATH=/app

# Run the preprocessor
CMD ["python", "src/preprocess.py"]