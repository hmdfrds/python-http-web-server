import json
import os
import sys


def load_config(config_file="config.json"):

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


if __name__ == "__main__":
    try:
        config = load_config()
        print("Configuration loaded successfully:")
        for key, value in config.items():
            print(f"    {key}: {value}")
    except Exception as e:
        print(f"Error loading configuration: {e}")
        sys.exit(1)
