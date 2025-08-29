from pyinfra import host
from pyinfra.operations import apt, files, server, systemd, pip

svc = host.data.service_name
user = host.data.service_user
app_dir = host.data.app_dir
port = host.data.listen_port

server.user(
    name="Create service user for camera app",
    user=host.data.service_user,
    home=f"/home/{host.data.service_user}",
    shell="/bin/bash",
    groups=["video"],
)


apt.packages(
    name="Install OS packages for Picamera2, Flask, and Python",
    packages=[
        "python3-pip",
        "libcamera-apps",
        "python3-libcamera",
        "python3-kms++",
        "python3-picamera2",
        "python3-flask",
        "libcap-dev",
    ],
    update=True,
    present=True,
)

files.directory(
    name="Create app directory",
    path=app_dir,
    user=user,
    group=user,
    mode="0755",
)

files.put(
    name="Upload application file",
    src="../cam/app.py",
    dest=f"{app_dir}/app.py",
    user=user,
    group=user,
    mode="0644",
)

server.shell(
    name="Ensure user is in 'video' group",
    commands=[f"id -nG {user} | grep -qw video || usermod -aG video {user}"],
)

# Install systemd unit
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

# server.reboot(name="Reboot to apply all changes", delay=5)
