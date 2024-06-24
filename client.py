import threading
import time
import pyperclip
import requests

class Client:
    def __init__(self, group_id, server_address, logger):
        self.group_id = group_id
        self.server_address = server_address
        self.logger = logger
        self.running = True

    def run(self):
        self.logger.info(f"Running client, connecting to {self.server_address}")
        threading.Thread(target=self.monitor_clipboard, daemon=True).start()
        self.register_with_server()
        
        # Keep the main thread running
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.logger.info("Stopping client...")
            self.running = False

    def monitor_clipboard(self):
        last_clipboard = ''
        while self.running:
            current_clipboard = pyperclip.paste()
            if current_clipboard != last_clipboard:
                last_clipboard = current_clipboard
                self.send_to_server(current_clipboard)
            time.sleep(0.5)  # Check clipboard every 0.5 seconds

    def register_with_server(self):
        try:
            response = requests.post(f"{self.server_address}/register", json={
                "group_id": self.group_id
            })
            if response.status_code == 200:
                self.logger.info("Registered with server successfully")
                threading.Thread(target=self.poll_server, daemon=True).start()
            else:
                self.logger.error(f"Failed to register with server. Status code: {response.status_code}")
        except requests.RequestException as e:
            self.logger.error(f"Error connecting to server: {e}")

    def poll_server(self):
        while self.running:
            try:
                response = requests.get(f"{self.server_address}/poll/{self.group_id}")
                if response.status_code == 200:
                    clipboard_content = response.json().get('content')
                    if clipboard_content:
                        pyperclip.copy(clipboard_content)
                        self.logger.info("Received new clipboard content from server")
                time.sleep(1)  # Poll every second
            except requests.RequestException as e:
                self.logger.error(f"Error polling server: {e}")
                time.sleep(5)  # Wait a bit longer before retrying after an error

    def send_to_server(self, content):
        try:
            response = requests.post(f"{self.server_address}/update", json={
                "group_id": self.group_id,
                "content": content
            })
            if response.status_code == 200:
                self.logger.info(f"Sent update to server: {content[:20]}...")
            else:
                self.logger.error(f"Failed to send update to server. Status code: {response.status_code}")
        except requests.RequestException as e:
            self.logger.error(f"Error sending update to server: {e}")