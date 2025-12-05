
#!/usr/bin/env python3
"""
Simple HTTP client for the lab.
Usage:
  python client.py <host> <port> <url_path> <save_directory>
Examples:
  python client.py localhost 8000 /index.html ./downloads
  python client.py localhost 8000 /books/book1.pdf ./downloads
"""
import socket, sys, os

def recv_all(sock):
    data = b''
    while True:
        part = sock.recv(4096)
        if not part:
            break
        data += part
    return data

def parse_response(resp):
    head, _, body = resp.partition(b'\r\n\r\n')
    headers = head.decode().split('\r\n')
    status = headers[0]
    hdrs = {}
    for h in headers[1:]:
        if ':' in h:
            k,v = h.split(':',1)
            hdrs[k.strip().lower()] = v.strip()
    return status, hdrs, body

if __name__ == '__main__':
    if len(sys.argv) < 5:
        print("Usage: client.py host port url_path save_dir")
        sys.exit(1)
    host, port, path, save_dir = sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4]
    if not path.startswith('/'):
        path = '/' + path
    os.makedirs(save_dir, exist_ok=True)
    req = f"GET {path} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n".encode()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        s.sendall(req)
        resp = recv_all(s)
    status, headers, body = parse_response(resp)
    print("Status:", status)
    ctype = headers.get('content-type','')
    if 'application/pdf' in ctype or 'image/' in ctype or path.endswith('.png') or path.endswith('.pdf'):
        # save binary
        filename = os.path.basename(path.rstrip('/')) or 'index'
        out = os.path.join(save_dir, filename)
        with open(out, 'wb') as f:
            f.write(body)
        print("Saved to", out)
    else:
        # print body as text
        try:
            print(body.decode())
        except:
            print(body)
