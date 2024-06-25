import argparse
import logging
from .server import create_server
from .client import Client
import os
import sys
from .installer import install_client, install_server

import yaml
from dataclasses import dataclass, asdict
from typing import Optional

@dataclass
class UniclipConfig:
    group_id: Optional[str] = None
    server_address: Optional[str] = None
    headless: bool = False

class ConfigManager:
    def __init__(self, config_dir='~/.config/uniclip'):
        self.config_dir = os.path.expanduser(config_dir)
        self.config_path = os.path.join(self.config_dir, 'config.yaml')

    def load_config(self) -> UniclipConfig:
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                config_dict = yaml.safe_load(f)
                return UniclipConfig(**config_dict)
        return UniclipConfig()

    def save_config(self, config: UniclipConfig):
        os.makedirs(self.config_dir, exist_ok=True)
        with open(self.config_path, 'w') as f:
            yaml.dump(asdict(config), f)

class UniclipApp:
    def __init__(self):
        self.config_manager = ConfigManager()
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger('Uniclip')

    def run(self):
        parser = argparse.ArgumentParser(description="Uniclip Clipboard Sync")
        subparsers = parser.add_subparsers(dest='mode', help='Operating mode')

        # Client parser (default)
        client_parser = subparsers.add_parser('client', help='Run in client mode')
        client_parser.add_argument('--group', help="Group ID for the client")
        client_parser.add_argument('--server', help="Server address for the client")
        client_parser.add_argument('--headless', action='store_true', help="Force headless mode for client")

        # Server subcommand
        server_parser = subparsers.add_parser('server', help='Run in server mode')
        server_subparsers = server_parser.add_subparsers(dest='server_command', help='Server commands')
        server_subparsers.add_parser('install', help='Install server as a systemd service')

        # Install subcommand
        subparsers.add_parser('install', help='Install client as a user-mode systemd service')

        # Parse arguments
        args = parser.parse_args()
        
        # If no subcommand was specified, default to 'client'
        if not args.mode:
            args.mode = 'client'
            # Re-parse arguments as client
            args = client_parser.parse_args(sys.argv[1:])

        config = self.config_manager.load_config()

        if args.mode == 'server':
            if args.server_command == 'install':
                install_server()
            else:
                server = create_server(self.logger)
                server.run()
        elif args.mode == 'client':
            group_id = args.group or config.group_id
            server_address = args.server or config.server_address
            headless = args.headless or config.headless
            if not group_id or not server_address:
                self.logger.error("Group ID and server address are required for client mode")
                return
            client = Client(group_id, server_address, self.logger, headless)
            client.run()
        elif args.mode == 'install':
            install_client()

def main():
    app = UniclipApp()
    app.run()

if __name__ == "__main__":
    main()