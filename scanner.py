#!/usr/bin/env python3
import socket
import sys

def scan_port(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(0.5)
    result = sock.connect_ex((host, port))
    sock.close()
    return result == 0

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <IP>")
        sys.exit(1)
    
    host = sys.argv[1]
    print(f"Scanning {host}...")
    
    for port in range(1, 1025):
        if scan_port(host, port):
            print(f"Port {port} is OPEN")
