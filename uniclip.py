import argparse
from config_manager import ConfigManager
from logger import Logger
from server import create_server
from client import Client

class UniclipApp:
    def __init__(self):
        self.config_manager = ConfigManager()
        self.logger = Logger()

    def run(self):
        parser = argparse.ArgumentParser(description="Uniclip Clipboard Sync")
        parser.add_argument('mode', choices=['client', 'server'], help="Operating mode")
        parser.add_argument('--group', help="Group ID for the client")
        parser.add_argument('--server', help="Server address for the client")
        args = parser.parse_args()

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

            client = Client(group_id, server_address, self.logger)
            client.run()
        else:
            self.logger.error(f"Invalid mode: {args.mode}")

if __name__ == "__main__":
    app = UniclipApp()
    app.run()
