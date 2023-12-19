#!/bin/python3
import time
import os
import subprocess
import threading
import socketserver
import atexit
import logging
import socket

openSockets = []
socketListLock = threading.Lock()
port = "/tmp/server.socket"
socketServer = None
openProcess = None

class SocketHandler (socketserver.BaseRequestHandler):
    def handle(self):
        logging.info(f"new socket connection from {self.client_address}")
        socketListLock.acquire()
        openSockets.append(self.request)
        socketListLock.release()
        while True:
            input = self.request.recv(1024)
            if not input:
                break
            if openProcess:
                openProcess.stdin.write(input)
                openProcess.stdin.flush()
        logging.info(f"closed connection from {self.client_address}")
        socketListLock.acquire()
        if self.request in openSockets:
            openSockets.remove(self.request)
        socketListLock.release()

def runSocketServer():
    global socketServer
    with socketserver.ThreadingUnixStreamServer(port, SocketHandler) as socketServer:
        atexit.register(closeSocketServer, port)
        socketServer.serve_forever()

def closeSocketServer(serverPort):
    os.unlink(serverPort)



serverThread = threading.Thread(target=runSocketServer, daemon=True)
serverThread.start()
logging.info("launching server")
with subprocess.Popen(["/home/resolute/minecrafttesting/server1/start.sh"],cwd="/home/resolute/minecrafttesting/server1",text=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin = subprocess.PIPE) as proc:
    openProcess = proc
    os.set_blocking(proc.stdout.fileno(), False)
    while proc.poll() == None:
        readline = proc.stdout.readline()
        logging.info(f"server: {readline}")
        for sock in openSockets:
            try:
                sock.sendall(readline)
            except BrokenPipeError as e:
                socketListLock.acquire()
                if sock in openSockets:
                    openSockets.remove(sock)
                socketListLock.release()
    retCode = proc.poll()
    print("server ended")
    openProcess = None
    for sock in openSockets:
        try:
            sock.sendall(b"server closed\n")
            sock.shutdown(socket.SHUT_RDWR)
            sock.close()
        except BrokenPipeError as e:
            socketListLock.acquire()
            if sock in openSockets:
                openSockets.remove(sock)
            socketListLock.release()
    socketServer.shutdown()
    exit(retCode) 
