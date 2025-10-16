# PR Lab 1 - HTTP file server (single-threaded)

## What is included
- `server.py` - single-threaded HTTP server using raw sockets (serves HTML, PNG, PDF; directory listing)
- `client.py` - simple HTTP client that saves PNG/PDF to a directory or prints HTML
- `site/` - content to serve (index.html, image.png, sample.pdf, nested `books/`)
- `Dockerfile` and `docker-compose.yml` to run the server

## How to run locally (without Docker)
1. Open a terminal in the project root.
2. Start server:
   ```
   python3 server.py 8000 site
   ```
3. Open http://localhost:8000/ in your browser.
4. Try requests:
   - `GET /` -> index.html with image
   - `GET /sample.pdf` -> PDF
   - `GET /image.png` -> PNG
   - `GET /books/` -> directory listing
   - `GET /nonexistent` -> 404

## Using the client
```
python3 client.py localhost 8000 /sample.pdf ./downloads
python3 client.py localhost 8000 /books/book1.pdf ./downloads
python3 client.py localhost 8000 / ./downloads
```

## Docker (how I configured)
- `docker-compose up --build` will build the image and run the server on port 8000, serving the `site/` directory.

## Notes / Lab requirements
- Server accepts and parses HTTP GET requests and responds with appropriate headers.
- Returns 404 for unknown files or unsupported extensions.
- Handles nested directories and generates directory listing (extra points).
- Simple client implemented (extra points).

