# Python HTTP Web Server  

A fully compliant HTTP/1.1 web server build from scratch using Python's standard libraries. This project demonstrates the internals of network programming, file I/O, multi-threading, and basic web security-all without relying on external packages.

## Feature

- **Static File Serving:** Serves HTML, CSS, JS, and other static files from a document root.
- **Directory Listing:** Automatically generates a directory listing when no `intex.html` is present.
- **HTTP Methods:** Supports GET and HEAD requests.
- **Custom Error Handling:** Custom 404 and 500 error pages.
- **Threading:** Handles concurrent clients using Python's `threading` module.
- **Admin Interface:** Separate web interface (with Basic Authentication) to monitor:
  - Total requests served
  - Current active connections (with client details)
  - Server uptime
  - Last 10 log entries
- **Configuration:** Loads settings from a JSON configuration file.
- **Logging:** Thread-safe logging of requests, errors, and periodic statistics.

## Project Structure

```text
http-web-server/
    ├── config.json         # Configuration file with server settings
    ├── server.py           # Main server initialization and accept-loop
    ├── request_handler.py  # HTTP request parsing and response generation
    ├── logger.py           # Thread-safe logging module
    ├── admin_interface.py  # Administrative web interface
    ├── utils.py            # Utility functions
    ├── www/                # Document root for static files
        ├── index.html      # Sample home page
```

## Setup

1. **Prerequisites:**

   - Python 3.9 or later
2. **Clone the Repository:**

    ```bash
    git clone https://github.com/hmdfrds/python-http-web-server 
    cd python-http-web-server
    ```

3. Configuration

    ```json
    {
    "host": "0.0.0.0",
    "port": 8080,
    "admin_port": 8081,
    "document_root": "./www",
    "max_threads": 50,
    "log_file": "./server.log"
    }
    ```

## Running the Server

Run the sever from the command line.

```bash
python server.py
```

The server will start listening on the configured port (default is 8080). The admin interface will be available on the admin port (default is 8081).


## Testing

- **Basic File Request:**
    Use a web browser or curl:

    ```bash
    curl -I http://localhost:8080/index.html
    curl http://localhost:8080/
    ```

- **Directory Listing:**
    Navigate to a URL coresponding to a directory that does not contain an `index.html` file to view the dynamically generated directory listing.
- **Error Handling:**
    Request a non-existent file to verify that the custom 404 error page is displayed.
- **Admin Interface:**
    Open your browser and go to [](http:/localhost:8081/). When prompted for credentials, use:
  - **Username:** `admin`
  - **Password:** `adminpass`

## Logging

The server logs each HTTP request, erors, and periodic server statistics to the file specified in `config.json` (default is `server.log`). Logging is thread-safe to ensure reliability under concurrent access.

## License

MIT License. See [License](LICENSE).
