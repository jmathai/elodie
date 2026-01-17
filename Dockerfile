# Base image with Python 3.11 slim
FROM python:3.11-slim

# Avoid interactive prompts and set UTF-8
ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ca-certificates \
        libimage-exiftool-perl \
        wget \
        make \
        locales && \
    locale-gen C.UTF-8 && \
    pip install --upgrade pip setuptools wheel && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /opt/elodie

# Copy Elodie requirements files
COPY requirements.txt .
COPY docs/requirements.txt docs/requirements.txt
COPY elodie/tests/requirements.txt elodie/tests/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r docs/requirements.txt && \
    pip install --no-cache-dir -r elodie/tests/requirements.txt && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the Elodie project
COPY . .

# Default command (interactive bash for debugging)
CMD ["/bin/bash"]

