import threading
import time
from datetime import datetime


class Logger:

    def __init__(self, log_file):
        """Initialize the logger.

        Parameters:
            log_file (str): The path to the log file.
        """
        self.log_file = log_file
        self.lock = threading.Lock()
        self.total_requests = 0
        self.active_connections = (
            {}
        )  # dict to track active connections, e.g., {client_ip: connection_time}
        self.start_time = datetime.now()

    def log(self, message):
        """Write a log message to the log file in a thread-safe manner

        Args:
            message (str): The message to log.
        """
        timestamp = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        with self.lock:
            with open(self.log_file, "a") as f:
                f.write(log_entry)

    def log_request(self, client_ip, request_line, response_code):
        """Log an HTTP request.

        Args:
            client_ip (str): The IP address of the client.
            request_line (str): The HTTP request line.
            response_code (int): The HTTP request code.
        """
        self.total_requests += 1
        message = (
            f"REQUEST from {client_ip}: '{request_line}' responded with {response_code}"
        )
        self.log(message)

    def log_error(self, error_message):
        """Log an error message.

        Args:
            error_message (str): A detailed error description.
        """
        self.log(f"ERROR: {error_message}")

    def log_stats(self):
        """Log periodic server statistics: total requests server, active connections, and uptime."""
        uptime = (datetime.now() - self.start_time).total_seconds()
        stats_message = (
            f"STATS: Total Request: {self.total_requests}, "
            f"Active Connections: {len(self.active_connections)},"
            f"Uptime: {uptime: .0f} seconds."
        )

    def start_periodic_stats(self, interval=60):

        def stats_loop():
            while True:
                time.sleep(interval)
                self.log_stats()

        stats_thread = threading.Thread(target=stats_loop, daemon=True)
        stats_thread = threading.Thread(target=stats_loop, daemon=True)


if __name__ == "__main__":

    test_logger = Logger("test_server.log")
    test_logger.log("This is a test log entry.")
    test_logger.log_request("127.0.0.1", "GET /index.html HTTP/1.1", 200)
    test_logger.log_error("This is a test error.")
    # Let the periodic stats log a couple of entries
    test_logger.start_periodic_stats(interval=5)
    time.sleep(15)
