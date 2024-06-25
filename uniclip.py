import argparse
import logging
from server import create_server
from client import Client
import json
import os

class ConfigManager:
    def __init__(self, config_path='~/.uniclip'):
        self.config_path = os.path.expanduser(config_path)

    def load_config(self):
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                return json.load(f)
        return {}

    def save_config(self, config):
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=2)


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

        # Parse arguments
        args, unknown = parser.parse_known_args()
        
        # If no subcommand was specified, default to 'client'
        if not args.mode:
            args.mode = 'client'
            # Re-parse arguments as client
            args = client_parser.parse_args(unknown)

        config = self.config_manager.load_config()

        if args.mode == 'server':
            server = create_server(self.logger)
            server.run()
        elif args.mode == 'client':
            group_id = args.group or config.get('group_id')
            server_address = args.server or config.get('server_address')
            if not group_id or not server_address:
                self.logger.error("Group ID and server address are required for client mode")
                return
            client = Client(group_id, server_address, self.logger, args.headless)
            client.run()

if __name__ == "__main__":
    app = UniclipApp()
    app.run()