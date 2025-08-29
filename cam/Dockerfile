FROM dtcooper/raspberrypi-os:python-bookworm

WORKDIR /app

# Install camera dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libcamera-apps \
    libcamera-dev \
    python3-libcamera \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN python3 -m pip install --no-cache-dir -r requirements.txt

COPY app.py .

EXPOSE 5000

CMD ["python3", "app.py"]
