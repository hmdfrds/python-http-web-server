from pathlib import Path


import os


def safe_path(document_root, request_path):
    """
    Resolve a safe file system path within the document root to prevent directory traversal attacks.

    Parameters:
        document_root (str): The base directory where static files are served from.
        request_path (str): The requested URL path (e.g., "/index.html" or "/subdir/file.txt").

    Returns:
        str: The absolute path to the requested file within the document root.

    Raises:
        ValueError: If the resolved path is outside of the document root.
    """
    # Remove any leading slashes from the requested path
    sanitized_path = request_path.lstrip("/")

    # Join the document_root and the sanitized request path
    requested_full_path = os.path.join(document_root, sanitized_path)

    # Normalize and convert to an absolute path
    requested_full_path = os.path.abspath(os.path.normpath(requested_full_path))
    document_root_abs = os.path.abspath(document_root)

    # Ensure that the requested path is within the document root
    if not requested_full_path.startswith(document_root_abs):
        raise ValueError("Invalid request path: directory traversal attempt detected.")

    return requested_full_path


def http_date_format(dt):
    """Format a datetime object int o an HTTP-date string as per RFC 7231

    Args:
        date (datatime.datetime): The datetime to format. If naive, it is assumed to be in UTC.

    Returns:
        str: The formatted HTTP date string (e.g., "Mon, 25 Feb 2025 14:30:00 GMT").
    """
    return dt.strftime("%a, %d %b %Y %H:%M:%S GMT")
