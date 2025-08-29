from pyinfra import host
from pyinfra.operations import apt, files, server, systemd, pip

svc = host.data.service_name
user = host.data.service_user
app_dir = host.data.app_dir
venv_dir = host.data.venv_dir
port = host.data.listen_port

apt.packages(
    name="Install OS packages for Picamera2 + Python",
    packages=[
        "python3-venv",
        "python3-pip",
        "libcamera-apps",
        "python3-libcamera",
        "python3-kms++",
        "python3-pyqt5",
        "python3-picamera2",
    ],
    update=True,
    sudo=True,
)

files.directory(
    name="Create app directory",
    path=app_dir,
    user=user,
    group=user,
    mode="0755",
    sudo=True,
)

files.put(
    name="Upload app.py",
    src="app/app.py",
    dest=f"{app_dir}/app.py",
    user=user,
    group=user,
    mode="0644",
    sudo=True,
)

files.put(
    name="Upload requirements.txt",
    src="app/requirements.txt",
    dest=f"{app_dir}/requirements.txt",
    user=user,
    group=user,
    mode="0644",
    sudo=True,
)

server.shell(
    name="Create venv if missing",
    commands=[f"test -d {venv_dir} || python3 -m venv {venv_dir}"],
    sudo=True,
)

pip.packages(
    name="Install Python requirements in venv",
    requirements=f"{app_dir}/requirements.txt",
    virtualenv=venv_dir,
    extra_install_args="--no-cache-dir",
    sudo=True,
)

server.shell(
    name="Ensure user is in 'video' group",
    commands=[f"id -nG {user} | grep -qw video || usermod -aG video {user}"],
    sudo=True,
)

# 6) Install systemd unit
files.template(
    name="Install systemd unit",
    src="deploy/homesec-cam.service.j2",
    dest=f"/etc/systemd/system/{svc}.service",
    user="root",
    group="root",
    mode="0644",
    svc=svc,
    user=user,
    app_dir=app_dir,
    venv_dir=venv_dir,
    port=port,
    sudo=True,
)

systemd.daemon_reload(
    name="Reload systemd",
    sudo=True,
)

systemd.service(
    name="Enable & start service",
    service=svc,
    running=True,
    enabled=True,
    restarted=True,
    sudo=True
)

# server.reboot(name="Reboot for group change", delay=5, sudo=True)
