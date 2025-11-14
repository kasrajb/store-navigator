# ────────────────────────────────────────────────────────────────────────────
# 1. Base image ‒ already contains RTAB-Map CLI binaries
# ────────────────────────────────────────────────────────────────────────────
# Use the newer Ubuntu 22.04 (Jammy) based image for daemon support
FROM introlab3it/rtabmap:jammy

# Suppress interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# ────────────────────────────────────────────────────────────────────────────
# Performance Optimizations for Headless RTAB-Map (Based on GitHub Issues #358, #1528)
# ────────────────────────────────────────────────────────────────────────────
# OpenCV I/O optimizations for better performance
ENV OPENCV_IO_MAX_IMAGE_PIXELS=2000000000
ENV OPENCV_IO_ENABLE_JASPER=OFF
ENV OPENCV_IO_ENABLE_OPENEXR=OFF

# Multi-threading control for deterministic performance (Issue #358)
ENV OMP_NUM_THREADS=1
ENV OPENCV_THREAD_COUNT=1

# ────────────────────────────────────────────────────────────────────────────
# 2. Install Python 3 and pip inside the Ubuntu image
# ────────────────────────────────────────────────────────────────────────────
# Install Python 3, pip, and setuptools
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        python3 \
        python3-pip \
        python3-setuptools && \
    pip3 install --no-cache-dir --upgrade pip && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# ────────────────────────────────────────────────────────────────────────────
# 3. Copy requirements and install them
# ────────────────────────────────────────────────────────────────────────────
# Set the working directory to /app
WORKDIR /app

# Copy requirements and install them
COPY requirements.txt /app/requirements.txt
RUN pip3 install --no-cache-dir -r /app/requirements.txt

# ────────────────────────────────────────────────────────────────────────────
# 4. Add unprivileged user and copy application code + embed data files
# ────────────────────────────────────────────────────────────────────────────
# Add unprivileged user
RUN useradd -ms /bin/bash appuser

# Copy all application files including data
COPY . /app

# ────────────────────────────────────────────────────────────────────────────
# IMPORTANT: Database handling for Railway deployment
# Railway: Database will be uploaded separately to persistent volume at /data/database.db
# Local: Database copied from data/database/ if available
# ────────────────────────────────────────────────────────────────────────────
RUN mkdir -p /data
# Copy database if it exists (for local builds), but don't fail if missing (Railway deployment)
RUN if [ -f /app/data/database/corridor-V3.db ]; then \
        cp /app/data/database/corridor-V3.db /data/database.db && \
        echo "Database copied from build context"; \
    else \
        echo "No database in build context - expecting external volume mount at /data/database.db"; \
    fi
# Test image is now external - no longer copied here

# Set proper ownership
RUN chown -R appuser:appuser /data
RUN chown -R appuser:appuser /app

# Switch to the unprivileged "appuser"
USER appuser

# ────────────────────────────────────────────────────────────────────────────
# 5. Expose port and launch FastAPI via Uvicorn
# ────────────────────────────────────────────────────────────────────────────
# Expose port 8000 for the API
EXPOSE 8000

# Start the FastAPI app
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
