from pyinfra import host
from pyinfra.operations import apt, files, server, systemd, pip

svc = host.data.service_name
user = host.data.service_user
app_dir = host.data.app_dir
venv_dir = host.data.venv_dir
port = host.data.listen_port

server.user(
    name="Create service user for camera app",
    user=host.data.service_user,  # comes from group_data/all.py
    home=f"/home/{host.data.service_user}",
    shell="/bin/bash",
    groups=["video"],     # so it can access /dev/video*
)

apt.packages(
    name="Install system packages for camera and Python",
    packages=[
        "python3-pip",
        "python3-picamera2",
        "libcamera-apps",
        "python3-libcamera",
        "python3-flask",
        "libcamera-apps",
        "libcap-dev",
    ],
    update=True,
)

files.directory(
    name="Create app directory",
    path=app_dir,
    user=user,
    group=user,
    mode="0755",
)

files.put(
    src="../cam/app.py",
    dest=f"{app_dir}/app.py",
    user=user,
    group=user,
    mode="0644",
)

files.put(
    name="Upload requirements.txt",
    src="../cam/requirements.txt",
    dest=f"{app_dir}/requirements.txt",
    user=user,
    group=user,
    mode="0644",
)

server.shell(
    name="Clean any conflicting pip packages",
    commands=[
        "python3 -m pip uninstall -y picamera2 || true",
        "rm -rf /opt/homesec-cam/.venv || true",
    ],
)

server.shell(
    name="Ensure user is in 'video' group",
    commands=[f"id -nG {user} | grep -qw video || usermod -aG video {user}"],
)

# 6) Install systemd unit
files.template(
    name="Install systemd unit",
    src="homesec-cam.service.j2",
    dest=f"/etc/systemd/system/{svc}.service",
    user="root",
    group="root",
    mode="0644",
    svc=svc,
    service_user=user,
    app_dir=app_dir,
    venv_dir=venv_dir,
    port=port,
)

systemd.daemon_reload(
    name="Reload systemd",
)

systemd.service(
    name="Enable & start service",
    service=svc,
    running=True,
    enabled=True,
    restarted=True,
)

# server.reboot(name="Reboot for group change", delay=5)
