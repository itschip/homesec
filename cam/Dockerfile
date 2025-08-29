FROM debian:bookworm-slim

WORKDIR /app

# Add Raspberry Pi repository and install camera dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    gnupg \
    && wget -O - https://archive.raspberrypi.org/debian/raspberrypi.gpg.key | apt-key add - \
    && echo "deb https://archive.raspberrypi.org/debian/ bookworm main" >> /etc/apt/sources.list \
    && apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-venv \
    libcamera-apps \
    libcamera-dev \
    python3-libcamera \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN python3 -m pip install --no-cache-dir -r requirements.txt

COPY app.py .

EXPOSE 5000

CMD ["python3", "app.py"]
