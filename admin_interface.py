import threading
import os
from datetime import datetime
import base64
import socket


class AdminInterface:

    def __init__(self, config, logger):
        self.host = config.get("host", "0.0.0.0")
        self.admin_port = config.get("admin_port", 8081)
        self.logger = logger
        # Hardcoded credentials:
        self.username = "admin"
        self.password = "adminpass"

    def start(self):
        thread = threading.Thread(target=self.run, daemon=True)
        thread.start()
        print(f"Admin interface is running on {self.host}:{self.admin_port}")

    def run(self):
        admin_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            admin_socket.bind((self.host, self.admin_port))
            admin_socket.listen(5)
        except Exception as e:
            print(
                f"Failed to bind admin interface on {self.host}:{self.admin_port}: {e}"
            )
            return
        while True:
            try:
                client_conn, client_addr = admin_socket.accept()
                threading.Thread(
                    target=self.handle_request,
                    args=(client_conn, client_addr),
                    daemon=True,
                ).start()
            except Exception as e:
                print(f"Admin interface error: {e}")

    def handle_request(self, client_conn, client_addr):
        """Process an incoming adming request, authenticate it, and send the HTML stats page."""
        try:
            request_data = client_conn.recv(1024).decode("utf-8")
            if not request_data:
                client_conn.close()
                return
            # Parse HTTP request headers
            lines = request_data.split("\r\n")
            headers = {}
            for line in lines[1:]:
                if not line:
                    break
                if ": " in line:
                    key, value = line.split(": ", 1)
                    headers[key] = value
            # Verify HTTP Basic Authentication

            if not self.is_authenticated(headers):
                response = "HTTP/1.1 401 Unauthorized\r\n"
                response += 'WWW-Authenticate: Basic realm="Admin Interface\r\n'
                response += "Content-Length: 0\r\n\r\n"
                client_conn.sendall(response.encode("utf-8"))
                client_conn.close()
                return

            # Generate admin page HTML content

            html = self.generate_admin_page()

            # Build response headers
            response_headers = "HTTP/1.1 200 OK\r\n"
            response_headers += "Content-Type: text/html\r\n"
            response_headers += f"Content-Length: {len(html.encode('utf-8'))}r\n"
            response_headers += "Connection: close\r\n\r\n"
            response = response_headers + html
            client_conn.sendall(response.encode("utf-8"))
        except Exception as e:
            print(f"Error handling admin request from {client_addr}: {e}")
        finally:
            client_conn.close()

    def is_authenticated(self, headers):
        """Check if the request contains valid HTTP Basic Authentication credentials.

        Args:
            headers (dict): The HTTP request headers

        Returns:
            bool: True if authenticated; False otherwise
        """
        auth_header = headers.get("Authorization", "")
        if auth_header.startswith("Basic "):
            encoded = auth_header.split(" ", 1)[1]
            try:
                decoded = base64.b64decode(encoded).decode("utf-8")
                # Expecting the format "username:password"
                if decoded == f"{self.username}:{self.password}":
                    return True
            except Exception:
                pass
        return False

    def generate_admin_page(self):
        """Generate the HTML content for the admin interface page. Display total reqeust, active connections, uptime, and the lat 10 log entries.

        Returns:
            _type_: _description_
        """
        total_reqeusts = self.logger.total_requests
        active_connections = self.logger.active_connections
        uptime = int((datetime.now() - self.logger.start_time).total_seconds())

        # Read the last 10 lines from the log file
        log_line = []
        try:
            if os.path.exists(self.logger.log_file):
                with open(self.logger.log_file, "r") as f:
                    all_lines = f.readlines()
                    log_lines = all_lines[-10:]
            else:
                log_lines = ["Log file not found."]

        except Exception:
            log_lines = ["Error reading log file."]

        # Build HTML content with embedded CSS and meta refresh
        html = "<html><head><title>Admin Interface</title>"
        html += "<meta http-equiv='refresh' content=30'>"
        html += (
            "<style>"
            "body { font-family: Arial, sans-serif; margin: 20px; }"
            "table { border-collapse: collapse; width: 80% }"
            "th, td { border: 1px solid #ddd; padding 8px; }"
            " th {background-color #f2f2f2; }"
            "</style>"
        )
        html += "</head><body>"
        html += "<h1>Admin Interface </h1>"
        html += f"<p><strong>Total Requests:</strong> {total_reqeusts}</p>"
        html += f"<p><strong>Server Uptime:</strong> {uptime} seconds</p>"
        html += "<h2>Active Connections</h2>"
        if active_connections:
            html += "<table><tr><th>Client IP</th><th>Connection Time</th><tr>"
            for ip, conn_time in active_connections.items():
                html += f"<tr><td>{ip}</td><td>{conn_time}</td></tr>"
            html += "</table>"
        else:
            html += "<p>No active connections.</p>"
        html += "<h2>Last 10 Log Entries</h2><pre>"
        for line in log_lines:
            html += line
        html += "</pre>"
        html += "</body></html>"
        return html
