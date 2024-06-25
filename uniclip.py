import argparse
from config_manager import ConfigManager
import logging
from server import create_server
from client import Client

class UniclipApp:
    def __init__(self):
        self.config_manager = ConfigManager()
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger('Uniclip')

    def run(self):
        # Change: Modified argument parsing to make client mode default
        parser = argparse.ArgumentParser(description="Uniclip Clipboard Sync")
        parser.add_argument('mode', nargs='?', default='client', choices=['client', 'server'], help="Operating mode (default: client)")
        parser.add_argument('--group', help="Group ID for the client")
        parser.add_argument('--server', help="Server address for the client")
        # Change: Added --headless argument
        parser.add_argument('--headless', action='store_true', help="Force headless mode for client")
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

            # Change: Pass headless argument to Client
            client = Client(group_id, server_address, self.logger, args.headless)
            client.run()
        else:
            self.logger.error(f"Invalid mode: {args.mode}")

if __name__ == "__main__":
    app = UniclipApp()
    app.run()
