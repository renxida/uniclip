import threading
import time
import os
import requests
import pyperclip
import socket
import uuid
class Client:
    # Change: Added force_headless parameter to __init__
    def __init__(self, group_id, server_address, logger, force_headless=False):
        self.group_id = group_id
        self.server_address = server_address
        self.logger = logger
        self.running = True
        self.clipboard_file = '/tmp/uniclip'
        self.force_headless = force_headless
        self.headless = self._detect_headless()
        self.client_id = self._generate_client_id()
        self.logger.debug(f"Client initialized with group_id: {group_id}, server_address: {server_address}, client_id: {self.client_id}, force_headless: {force_headless}")

    def _generate_client_id(self):
        hostname = socket.gethostname()
        short_uuid = str(uuid.uuid4())[:4]
        return f"{hostname}-{short_uuid}"

    def _detect_headless(self):
        # Change: Use force_headless if set
        if self.force_headless:
            self.logger.info("Forced headless mode")
            return True
        try:
            pyperclip.paste()
            self.logger.debug("Pyperclip successfully detected copy/paste mechanism")
            return False
        except pyperclip.PyperclipException:
            self.logger.info("Pyperclip couldn't find a copy/paste mechanism. Switching to headless mode.")
            return True

    def run(self):
        self.logger.info(f"Running client in {'headless' if self.headless else 'normal'} mode, connecting to {self.server_address}")
        if self.headless:
            self.logger.debug("Starting clipboard file monitoring thread")
            threading.Thread(target=self.monitor_clipboard_file, daemon=True).start()
        else:
            self.logger.debug("Starting clipboard monitoring thread")
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
        self.logger.debug(f"Starting to monitor clipboard file: {self.clipboard_file}")
        while self.running:
            try:
                current_modified = os.path.getmtime(self.clipboard_file)
                if current_modified != last_modified:
                    last_modified = current_modified
                    with open(self.clipboard_file, 'r') as f:
                        content = f.read()
                    self.logger.debug(f"Clipboard file changed. New content: {content[:50]}...")
                    self.send_to_server(content)
            except FileNotFoundError:
                self.logger.debug(f"Clipboard file not found. Creating: {self.clipboard_file}")
                open(self.clipboard_file, 'a').close()
            except Exception as e:
                self.logger.error(f"Error monitoring clipboard file: {e}")
            time.sleep(0.5)  # Check file every 0.5 seconds

    def monitor_clipboard(self):
        last_clipboard = ''
        self.logger.debug("Starting to monitor system clipboard")
        while self.running:
            try:
                current_clipboard = pyperclip.paste()
                if current_clipboard != last_clipboard:
                    self.logger.debug(f"Clipboard content changed. New content: {current_clipboard[:50]}...")
                    last_clipboard = current_clipboard
                    self.send_to_server(current_clipboard)
            except pyperclip.PyperclipException as e:
                self.logger.error(f"Error accessing clipboard: {e}")
                self.logger.info("Switching to headless mode")
                self.headless = True
                self.logger.debug("Starting clipboard file monitoring thread")
                threading.Thread(target=self.monitor_clipboard_file, daemon=True).start()
                break
            time.sleep(0.5)  # Check clipboard every 0.5 seconds

    def register_with_server(self):
        self.logger.debug(f"Attempting to register with server: {self.server_address}")
        try:
            response = requests.post(f"{self.server_address}/register", json={
                "group_id": self.group_id,
                "client_id": self.client_id
            })
            if response.status_code == 200:
                self.logger.info("Registered with server successfully")
                self.logger.debug("Starting server polling thread")
                threading.Thread(target=self.poll_server, daemon=True).start()
            else:
                self.logger.error(f"Failed to register with server. Status code: {response.status_code}")
        except requests.RequestException as e:
            self.logger.error(f"Error connecting to server: {e}")

    def poll_server(self):
        self.logger.debug("Starting to poll server for updates")
        while self.running:
            try:
                self.logger.debug(f"Polling server: {self.server_address}/poll/{self.group_id}/{self.client_id}")
                response = requests.get(f"{self.server_address}/poll/{self.group_id}/{self.client_id}")
                if response.status_code == 200:
                    data = response.json()
                    clipboard_content = data.get('content')
                    if clipboard_content:
                        self.logger.debug(f"Received new content from server: {clipboard_content[:50]}...")
                        if self.headless:
                            self.update_clipboard_file(clipboard_content)
                        else:
                            try:
                                pyperclip.copy(clipboard_content)
                                self.logger.debug("Successfully copied new content to clipboard")
                            except pyperclip.PyperclipException as e:
                                self.logger.error(f"Error copying to clipboard: {e}")
                                self.logger.info("Switching to headless mode")
                                self.headless = True
                                self.update_clipboard_file(clipboard_content)
                        self.logger.info("Received new clipboard content from server")
                    else:
                        self.logger.debug("No new content received from server")
                else:
                    self.logger.warning(f"Unexpected status code from server: {response.status_code}")
                time.sleep(0.5)  # Poll every 0.5 seconds
            except requests.RequestException as e:
                self.logger.error(f"Error polling server: {e}")
                time.sleep(5)  # Wait 5 seconds before retrying

    def send_to_server(self, content):
        self.logger.debug(f"Sending update to server: {content[:50]}...")
        try:
            response = requests.post(f"{self.server_address}/update", json={
                "group_id": self.group_id,
                "client_id": self.client_id,
                "content": content
            })
            if response.status_code == 200:
                self.logger.info(f"Sent update to server: {content[:20]}...")
            else:
                self.logger.error(f"Failed to send update to server. Status code: {response.status_code}")
        except requests.RequestException as e:
            self.logger.error(f"Error sending update to server: {e}")

    def update_clipboard_file(self, content):
        self.logger.debug(f"Updating clipboard file with new content: {content[:50]}...")
        try:
            with open(self.clipboard_file, 'w') as f:
                f.write(content)
            self.logger.debug("Clipboard file updated successfully")
        except Exception as e:
            self.logger.error(f"Error updating clipboard file: {e}")
