#!/bin/python3
import time
import os
import re
import argparse
import socket
import threading

parser = argparse.ArgumentParser(prog="closeServer.py", description="Server Closer")
parser.add_argument("--server", "-s", type=str, default="server") 
args = parser.parse_args() 
port = "/tmp/" + args.server + ".socket"

print("stoping server\n")
sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
sock.connect(port)

minutesToRestart = 1

string = f"/say I'm restarting in about {minutesToRestart} minutes\n"
sock.sendall(string.encode())

time_end = time.time() + 60* minutesToRestart
socketLock = threading.Lock()

def watchForPlayersEnterring(socket):
    prettyOpen = sock.makefile()
    line = prettyOpen.readline()
    match = re.match(r".* (?P<username>\w+)\[.*\] logged in with entity id", line)
    if match:
        string = f"/say Hey {match.group('username')}, I'm restarting in about {round((time_end-time.time())/60)} minutes\n"
        socketLock.acquire()
        sock.sendall(string.encode())
        socketLock.release()

thread = threading.Thread(target = watchForPlayersEnterring, args=(sock,), daemon=True)
thread.start()

while time.time() < time_end:
    pass

socketLock.acquire()
sock.sendall(b"/kick @a Server Daily Restart\n")
sock.close()
# this script doesn't actually stop the server. It just kicks everyone at the right time


