import threading
import time
import os
import requests
import pyperclip

class Client:
    def __init__(self, group_id, server_address, logger):
        self.group_id = group_id
        self.server_address = server_address
        self.logger = logger
        self.running = True
        self.clipboard_file = '/tmp/uniclip'
        self.headless = self._detect_headless()

    def _detect_headless(self):
        try:
            pyperclip.paste()
            return False
        except pyperclip.PyperclipException:
            self.logger.info("Pyperclip couldn't find a copy/paste mechanism. Switching to headless mode.")
            return True

    def run(self):
        self.logger.info(f"Running client in {'headless' if self.headless else 'normal'} mode, connecting to {self.server_address}")
        if self.headless:
            threading.Thread(target=self.monitor_clipboard_file, daemon=True).start()
        else:
            threading.Thread(target=self.monitor_clipboard, daemon=True).start()
        self.register_with_server()
        
        # Keep the main thread running
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.logger.info("Stopping client...")
            self.running = False

    def monitor_clipboard_file(self):
        last_modified = 0
        while self.running:
            try:
                current_modified = os.path.getmtime(self.clipboard_file)
                if current_modified != last_modified:
                    last_modified = current_modified
                    with open(self.clipboard_file, 'r') as f:
                        content = f.read()
                    self.send_to_server(content)
            except FileNotFoundError:
                # Create the file if it doesn't exist
                open(self.clipboard_file, 'a').close()
            except Exception as e:
                self.logger.error(f"Error monitoring clipboard file: {e}")
            time.sleep(0.5)  # Check file every 0.5 seconds

    def monitor_clipboard(self):
        last_clipboard = ''
        while self.running:
            try:
                current_clipboard = pyperclip.paste()
                if current_clipboard != last_clipboard:
                    last_clipboard = current_clipboard
                    self.send_to_server(current_clipboard)
            except pyperclip.PyperclipException as e:
                self.logger.error(f"Error accessing clipboard: {e}")
                self.logger.info("Switching to headless mode")
                self.headless = True
                threading.Thread(target=self.monitor_clipboard_file, daemon=True).start()
                break
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
                        if self.headless:
                            self.update_clipboard_file(clipboard_content)
                        else:
                            try:
                                pyperclip.copy(clipboard_content)
                            except pyperclip.PyperclipException as e:
                                self.logger.error(f"Error copying to clipboard: {e}")
                                self.logger.info("Switching to headless mode")
                                self.headless = True
                                self.update_clipboard_file(clipboard_content)
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

    def update_clipboard_file(self, content):
        try:
            with open(self.clipboard_file, 'w') as f:
                f.write(content)
        except Exception as e:
            self.logger.error(f"Error updating clipboard file: {e}")