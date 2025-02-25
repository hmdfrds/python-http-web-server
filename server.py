import json
import os
import sys
import socket
import threading
from request_handler import HTTPRequestHandler
from logger import Logger


def load_config(config_file="config.json"):
    """Loads and validates the configuration from a JSON file.

    Args:
        config_file (str, optional): Path to the confiugration file. Defaults to "config.json".

    Raises:
        FileNotFoundError: If the confiugration file does not exist.

    Returns:
        dict: Dictionary of config data.
    """

    if not os.path.exists(config_file):
        raise FileNotFoundError(f"Configuration file'{config_file}' not found.")

    with open(config_file, "r") as f:
        try:
            config = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format in '{config_file}': {e}")

    # List of required fields
    required_fields = [
        "host",
        "port",
        "admin_port",
        "document_root",
        "max_threads",
        "log_file",
    ]

    # Validate presence of required fields
    for field in required_fields:
        if field not in config:
            raise ValueError(f"Missing required configuration field: '{field}'")

    # Validate field types
    if not isinstance(config["port"], int):
        raise ValueError("The 'port' field must be an integer")
    if not isinstance(config["admin_port"], int):
        raise ValueError("The 'admin_port' field must be an integer.")
    if not isinstance(config["max_threads"], int):
        raise ValueError("The 'max_threads' field must be an integer.")

    if not os.path.isdir(config["document_root"]):
        raise ValueError(
            f"Document root '{config['document_root']}' is not a valid directory."
        )

    return config


def start_server(config, logger):
    """Set up the TCP socket, listen for incoming connections, and spawn a new thread for each connection.

    Args:
        config (dict): Configuration file loaded when the server start.
        logger (Logger): log instance.
    """
    host = config["host"]
    port = config["port"]
    max_threads = config["max_threads"]

    # Create a TCP socket. (Address Family - Internet) (Socket Type - Stream-based)
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server_socket.bind((host, port))
        server_socket.listen(max_threads)
        print(f"HTTP Server is listening on {host}:{port}")
        logger.log(f"Server started on {host}:{port}")

        # Main accept-loop
        while True:
            try:
                client_conn, client_addr = server_socket.accept()
                print(f"Accepted connection from {client_addr[0]}")
                # Spawn a new thread to handler the client connection.
                thread = threading.Thread(
                    target=HTTPRequestHandler.handle_client,
                    args=(client_conn, client_addr, config, logger),
                    daemon=True,
                )
                thread.start()
            except Exception as e:
                logger.log_error(f"Error handling connection: {e}")
    except Exception as e:
        logger.log_error(f"Server socket error: {e}")
    finally:
        server_socket.close()


if __name__ == "__main__":

    try:
        config = load_config()
        print("Configuration loaded successfully:")
        for key, value in config.items():
            print(f"    {key}: {value}")
    except Exception as e:
        print(f"Error loading configuration: {e}")
        sys.exit(1)

    logger = Logger(config["log_file"])
    logger.start_periodic_stats()  # Start stats logging every 60 seconds

    # Start the HTTP server
    start_server(config, logger)
