#!/bin/python3
import os
import sys
import socket
import atexit
import threading
import argparse

port = "/tmp/server.socket"

def inputLoop(sock):
    while True:
        data = sys.stdin.readline()
        sock.sendall(data.encode())

def outputLoop(sock):
    while True:
        data = sock.recv(4096)
        if not data:
           break
        sys.stdout.write(data.decode())

def closeSocket(sock):
    sock.close()

def main():
    parser = argparse.ArgumentParser(prog="closeServer.py", description="Server Closer")
    parser.add_argument("--server", "-s", type=str, default="server") 
    args = parser.parse_args() 
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.connect(port)
    if args.server != "server":
        sock.sendall(f"console {args.server}\n".encode())
    atexit.register(closeSocket, sock)

    print("Server Console Opened [Use ctr + C to exit]")
    inputThread = threading.Thread(target=inputLoop,args=(sock,), daemon=True)
    inputThread.start()
    try:
        outputLoop(sock)
    except KeyboardInterrupt:
        print("closing terminal")


if __name__ == "__main__":
    main()
