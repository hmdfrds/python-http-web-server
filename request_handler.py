import mimetypes
from utils import http_date_format, safe_path
from datetime import datetime
import os


class HTTPRequestHandler:

    def __init__(self, client_conn, client_addr, config, logger):
        """Initialize the request handler.

        Args:
            client_conn (socket.socket): The client socket connection.
            client_addr (tuple): The client's address.
            config (dict): Configuration parameters.
            logger (Logger): The logger instance.
        """
        self.client_conn = client_conn
        self.client_addr = client_addr
        self.config = config
        self.logger = logger
        self.document_root = config["document_root"]

    def handle(self):
        """Main handler for the HTTP request."""
        try:
            request_data = self.client_conn.recv(1024).decode("utf-8")
            if not request_data:
                self.client_conn.close()
                return

            # Parse the HTTP request line to be in the form "METHOD path HTTP/1.1"
            request_line, headers = self.parse_request(request_data)

            # Expecting the request line to be in the form "METHOD path HTTP/1.1"
            parts = request_line.split()
            if len(parts) != 3:
                raise ValueError("Invalid HTTP request line")
            method, path, version = parts

            # Sanitize and resolve t he requested path (prevent diretory traversal)

            full_path = safe_path(self.document_root, path)

            if method == "GET":
                self.handle_get(full_path, version, headers, request_line)
            elif method == "HEAD":
                self.handle_head(full_path, version, headers, request_line)
            else:
                # Method Not Allowed
                self.send_response(
                    405,
                    {"Content-Type": "text/html"},
                    "<html><body><h1>405 Method Not Allowed</h1></body></html>",
                )
                self.logger.log_request(self.client_addr[0], request_line, 405)
        except Exception as e:
            self.logger.log_error(
                f"Error handling request from {self.client_addr[0]}: {e}"
            )
            try:
                self.send_response(
                    500,
                    {"Content-Type": "text/html"},
                    "<html><body><h1>500 Internal Server Error</h1></body></html>",
                )
            except Exception:
                pass
        finally:
            self.client_conn.close()

    def parse_request(self, request_data):
        """Parse the raw HTTP request.

        Args:
            request_data (str): The raw HTTP request string.

        Returns:
            tuple: (request_line, headers_dict)
        """
        lines = request_data.split("\r\n")
        request_line = lines[0]
        headers = {}
        for line in lines[1:]:
            if line == "":
                break  # End of headers
            parts = line.split(":", 1)
            if len(parts) == 2:
                headers[parts[0].strip()] = parts[1].strip()
        return request_line, headers

    def handle_get(self, full_path, version, headers, request_line):
        """Process a GET request.

        Args:
            full_path (str): The resolved file system path.
            version (str): HTTP version.
            headers (dict): HTTP headers.
            request_line (str): The originial request line.
        """
        if os.path.isdir(full_path):
            # Check for index.html inside the directory
            index_path = os.path.join(full_path, "index.html")
            if os.path.exists(index_path):
                self.serve_file(index_path, version, request_line)
            else:
                # Generate directory listing if no index.html exists
                content = self.generate_directory_listing(full_path)
                self.send_response(
                    200,
                    {
                        "Content-Type": "text/html",
                        "Content-Length": str(len(content)),
                        "Date": http_date_format(datetime.now()),
                        "Server": "NoohHTTP/1.0",
                        "Connection": "close",
                    },
                    content,
                )
                self.logger.log_request(self.client_addr[0], request_line, 200)
        elif os.path.isfile(full_path):
            self.serve_file(full_path, version, request_line)
        else:
            # File or directory not found
            self.send_response(
                404,
                {
                    "Content-Type": "text/html",
                    "Date": http_date_format(datetime.now()),
                    "Server": "NoobHTTP/1.0",
                    "Connection": "close",
                },
                "<html><body><h1>404 Not Found</h1></body></html>",
            )
            self.logger.log_request(self.client_addr[0], request_line, 404)

    def handle_head(self, full_path, version, headers, request_line):
        """Process a HEAD request (same as GET but only headers are sent)

        Args:
            full_path (str): The resolved file system path.
            version (str): HTTP version.
            headers (dict): HTTP headers.
            request_line (str): The original request line.
        """
        if os.path.isdir(full_path):
            index_path = os.path.join(full_path, "index.html")
            if os.path.exists(index_path):
                self.serve_file(index_path, version, request_line, head_only=True)
            else:
                content = self.generate_directory_listing(full_path)
                self.send_response(
                    200,
                    {
                        "Content-Type": "text/html",
                        "Content-Length": str(len(content)),
                        "Date": http_date_format(datetime.now()),
                        "Server": "NoobHTTP/1.0",
                        "Connection": "close",
                    },
                    head_only=True,
                )
                self.logger.log_request(self.client_addr[0], request_line, 200)
        elif os.path.isfile(full_path):
            self.serve_file(full_path, version, request_line, head_only=True)
        else:
            self.send_response(
                404,
                {
                    "Content-Type": "text/html",
                    "Date": http_date_format(datetime.now()),
                    "Server": "NoobHTTP/1.0",
                    "Connection": "close",
                },
                head_only=True,
            )
            self.logger.log_request(self.client_addr[0], request_line, 404)

    def serve_file(self, file_path, version, request_line, head_only=False):
        """Serve a static file with appropriate headers.

        Args:
            file_path (str): The file path to serve.
            version (str): HTTP version.
            request_line (str): The original request line.
            head_only (bool, optional): If True, send only headers without body. Defaults to False.
        """
        try:
            with open(file_path, "rb") as f:
                content = f.read()
            mime_type, _ = mimetypes.guess_type(file_path)
            if not mime_type:
                mime_type = "application/octet-stream"
            headers = {
                "Content-Type": mime_type,
                "Content-Length": str(len(content)),
                "Date": http_date_format(datetime.now()),
                "Server": "NoobHTTP/1.0",
                "Connection": "close",
            }

            if head_only:
                self.send_response(200, headers, head_only=True)
            else:
                self.send_response(200, headers, content)
            self.logger.log_request(self.client_addr[0], request_line, 200)
        except Exception as e:
            self.logger.log_error(f"Error serving file '{file_path}': {e}")
            self.send_response(
                500,
                {
                    "Content-Type": "text/html",
                    "Date": http_date_format(datetime.now()),
                    "Server": "NoobHTTP/1.0",
                    "Connection": "close",
                },
                "<html><body><h1>500 Internal Server Error</h1></body></html>",
            )
            self.logger.log_request(self.client_addr[0], request_line, 500)

    def send_response(self, status_code, headers, body=None, head_only=False):
        """Format and send an HTTP response.

        Args:
            status_code (int): The HTTP status code.
            headers (dict): Response headers.
            body (str or bytes, optional): The response body. Defaults to None.
            head_only (bool, optional): If True, do not send the body. Defaults to False.
        """
        reason_phrases = {
            200: "OK",
            404: "Not Found",
            405: "Method Not Allowed",
            500: "Internal Server Error",
        }
        reason = reason_phrases.get(status_code, "")
        response_line = f"HTTP/1.1 {status_code} {reason}\r\n"

        header_lines = ""
        for header, value in headers.items():
            header_lines += f"{header}: {value}\r\n"

        # End of headers
        full_response = response_line + header_lines + "\r\n"

        try:
            self.client_conn.sendall(full_response.encode("utf-8"))
            if not head_only and body is not None:
                if isinstance(body, str):
                    self.client_conn.sendall(body.encode("utf-8"))
                else:
                    self.client_conn.sendall(body)
        except Exception as e:
            self.logger.log_error(f"Error sending response: {e}")

    def generate_directory_listing(self, directory_path):
        """Generate an HTML page listing files and directories.

        Args:
            directory_path (str): The direcotry to list

        Returns:
            str: The HTML content of the directory listing.
        """
        try:
            entries = os.listdir(directory_path)
            listing = "<html><head><title>Directory Listing</title></head><body>"
            listing += f"<h1>Directory listing for {directory_path}</h1><ul>"
            for entry in entries:
                full_entry_path = os.path.join(directory_path, entry)
                display_name = f"{entry}/" if os.path.isdir(full_entry_path) else entry
                modified_item = datetime.fromtimestamp(
                    os.path.getmtime(full_entry_path)
                ).strftime("%d-%m-%Y %H:%M:%S")
                listing += f"<li>{display_name} - Last Modified: {modified_item}</li>"
            listing += "</ul></body></html>"
            return listing
        except Exception as e:
            self.logger.log_error(
                f"Error generating directory listing for '{directory_path}': {e}"
            )
            return "<html><body><h1>500 Internal Server Error</h1></body></html>"

    @staticmethod
    def handle_client(client_conn, client_addr, config, logger):
        handler = HTTPRequestHandler(client_conn, client_addr, config, logger)
        handler.handle()
