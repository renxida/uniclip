import os
import sys
import platform
import subprocess

def install_client():
    if platform.system() != 'Linux':
        print("Error: Client installation is only supported on Linux systems.")
        sys.exit(1)

    # Create service content (unchanged)
    service_content = f"""[Unit]
Description=Uniclip Client Service
After=network.target

[Service]
ExecStart={sys.executable} {os.path.abspath(sys.argv[0])} client
Restart=always
User={os.getlogin()}

[Install]
WantedBy=default.target
"""

    # Install systemd service
    service_path = os.path.expanduser('~/.config/systemd/user/uniclip-client.service')
    os.makedirs(os.path.dirname(service_path), exist_ok=True)
    with open(service_path, 'w') as f:
        f.write(service_content)

    # Copy example config file
    config_dir = os.path.expanduser('~/.config/uniclip')
    os.makedirs(config_dir, exist_ok=True)
    example_config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.yml')
    config_path = os.path.join(config_dir, 'config.yml')
    
    if not os.path.exists(config_path):
        shutil.copy2(example_config_path, config_path)
        print(f"Example configuration file copied to {config_path}")
        print("Please edit this file to set your group ID and server address.")
    else:
        print(f"Configuration file already exists at {config_path}")
        print("New example configuration was not copied to avoid overwriting your settings.")

    # Enable and start the service
    subprocess.run(['systemctl', '--user', 'enable', 'uniclip-client.service'], check=True)
    subprocess.run(['systemctl', '--user', 'start', 'uniclip-client.service'], check=True)

    print("Uniclip client has been installed and started as a user-mode systemd service.")


def install_server():
    if platform.system() != 'Linux':
        print("Error: Server installation is only supported on Linux systems.")
        sys.exit(1)

    if os.geteuid() != 0:
        print("Error: Server installation requires root privileges. Please run with sudo.")
        sys.exit(1)

    service_content = f"""[Unit]
Description=Uniclip Server Service
After=network.target

[Service]
ExecStart={sys.executable} {os.path.abspath(sys.argv[0])} server
Restart=always
User=nobody

[Install]
WantedBy=multi-user.target
"""

    service_path = '/etc/systemd/system/uniclip-server.service'
    with open(service_path, 'w') as f:
        f.write(service_content)

    subprocess.run(['systemctl', 'enable', 'uniclip-server.service'], check=True)
    subprocess.run(['systemctl', 'start', 'uniclip-server.service'], check=True)

    print("Uniclip server has been installed and started as a system-wide systemd service.")