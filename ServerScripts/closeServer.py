#!/bin/python3
import time
import os
import socket
import argparse

def main():
    parser = argparse.ArgumentParser(prog="closeServer.py", description="Server Closer")
    parser.add_argument("--server", "-s", type=str, default="server") 
    args = parser.parse_args() 
    port = "/tmp/" + args.server + ".socket"
    print("stoping server")
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.connect(port)
    sock.sendall(b"/say I'm shutting down now!\n")
    time.sleep(10)
    sock.sendall(b"/stop\n")
    time.sleep(10)
    sock.close()



if __name__ == "__main__":
    main()