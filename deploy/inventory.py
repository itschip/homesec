hosts = ["chip@rpicam2.local"]

group_data = {
    "all": {
        "service_name": "homesec-cam",
        "service_user": "pi",
        "app_dir": "/opt/homesec-cam",
        "venv_dir": "/opt/homesec-cam/.venv",
        "listen_port": 5000,
    }
}
