
#!/usr/bin/env python3
"""
Simple single-threaded HTTP file server using raw TCP sockets.
Usage: python server.py <port> <directory>
Example: python server.py 8000 site
"""
import socket, sys, os, urllib.parse, mimetypes

mimetypes.init()
def guess_mime(path):
    if path.endswith('.html') or path.endswith('.htm'):
        return 'text/html; charset=utf-8'
    t, _ = mimetypes.guess_type(path)
    return t or 'application/octet-stream'

def make_response(status_code, reason, headers=None, body=b''):
    hdrs = headers or {}
    hdr_lines = ''.join(f"{k}: {v}\r\n" for k,v in hdrs.items())
    return f"HTTP/1.1 {status_code} {reason}\r\n".encode() + hdr_lines.encode() + b"\r\n" + body

def sanitize_path(path):
    # prevent directory traversal
    path = urllib.parse.unquote(path)
    if '?' in path:
        path = path.split('?',1)[0]
    if path.startswith('/'):
        path = path[1:]
    # collapse ..
    parts = []
    for p in path.split('/'):
        if p == '..':
            if parts:
                parts.pop()
        elif p and p != '.':
            parts.append(p)
    return os.path.join(*parts) if parts else ''

def directory_listing(fullpath, relpath):
    items = os.listdir(fullpath)
    body = ["<html><body><h1>Index of /{}</h1><ul>".format(relpath)]
    # parent link
    if relpath:
        parent = '/' + '/'.join(relpath.strip('/').split('/')[:-1])
        if not parent.endswith('/'):
            parent += '/'
        body.append(f'<li><a href="{parent}">../</a></li>')
    for name in sorted(items):
        display = name + ('/' if os.path.isdir(os.path.join(fullpath, name)) else '')
        href = '/' + os.path.join(relpath, name).replace('\\','/')
        if os.path.isdir(os.path.join(fullpath, name)):
            href += '/'
        body.append(f'<li><a href="{href}">{display}</a></li>')
    body.append("</ul></body></html>")
    return '\n'.join(body).encode('utf-8')

def handle_request(conn, base_dir):
    try:
        data = conn.recv(65536)
        if not data:
            return
        request_line = data.split(b'\r\n',1)[0].decode()
        parts = request_line.split()
        if len(parts) < 2:
            conn.sendall(make_response(400, "Bad Request"))
            return
        method, target = parts[0], parts[1]
        if method != 'GET':
            conn.sendall(make_response(405, "Method Not Allowed", {'Allow':'GET'}))
            return
        # sanitize
        rel = sanitize_path(target)
        fs_path = os.path.join(base_dir, rel)
        if os.path.isdir(fs_path):
            # ensure trailing slash - redirect
            if not target.endswith('/'):
                location = target + '/'
                conn.sendall(make_response(301, "Moved Permanently", {'Location': location}, b''))
                return
            body = directory_listing(fs_path, rel)
            headers = {'Content-Type': 'text/html; charset=utf-8', 'Content-Length': str(len(body))}
            conn.sendall(make_response(200, "OK", headers, body))
            return
        if not os.path.exists(fs_path) or not fs_path.startswith(os.path.abspath(base_dir)):
            body = b"<h1>404 Not Found</h1>"
            conn.sendall(make_response(404, "Not Found", {'Content-Type':'text/html; charset=utf-8', 'Content-Length': str(len(body))}, body))
            return
        # only allow html, png, pdf as per lab
        allowed = ('.html','.htm','.png','.pdf')
        if not fs_path.lower().endswith(allowed):
            body = b"<h1>404 Not Found</h1>"
            conn.sendall(make_response(404, "Not Found", {'Content-Type':'text/html; charset=utf-8', 'Content-Length': str(len(body))}, body))
            return
        with open(fs_path, 'rb') as f:
            content = f.read()
        ctype = guess_mime(fs_path)
        headers = {'Content-Type': ctype, 'Content-Length': str(len(content))}
        conn.sendall(make_response(200, "OK", headers, content))
    except Exception as e:
        try:
            body = f"<h1>500 Internal Server Error</h1><pre>{e}</pre>".encode('utf-8')
            conn.sendall(make_response(500, "Internal Server Error", {'Content-Type':'text/html; charset=utf-8','Content-Length':str(len(body))}, body))
        except:
            pass

def run_server(port, base_dir):
    base_dir = os.path.abspath(base_dir)
    print("Serving", base_dir, "on port", port)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('0.0.0.0', port))
        s.listen(5)
        while True:
            conn, addr = s.accept()
            with conn:
                print("Connection from", addr)
                handle_request(conn, base_dir)

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: server.py <port> <directory>")
        sys.exit(1)
    run_server(int(sys.argv[1]), sys.argv[2])
