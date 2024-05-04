#!/bin/python3
import time
import os
import subprocess
import threading
import socketserver
import atexit
import logging
import socket
import utils.serverConfig as serverConfig
import shlex
import argparse
import json
import signal
import re

startUpDelaySeconds = 5*60
shutdownWaitTimeSeconds = 5*60 # time to wait before soft kill
killWaitTimeSeconds = 60  # time to wait after soft for hard kill

startUpWaitTime = 5*60

openSockets: "dict[str, list[socket.socket]]" = dict()
socketListLock: "dict[str, threading.Lock]" = dict()
serverInputLock: "dict[str, threading.Lock]" = dict()

port = "/tmp/server.socket"
socketServer = None
openProcess = dict()
serverStatus = dict()
serverThreads = dict()

wrapperStop = False



def catchSigTerm(signmum, frame):
    logging.info("recieved Sig term")
    for server in serverStatus:
        if serverStatus[server] != "OFF":
            writeToServer(server, b"/say Stoping Server\n")
    time.sleep(5)
    waitingThreads = {}
    for server in serverStatus:
        if serverStatus[server] != "OFF":
            serverStatus[server] = "STOPPING"
            sendStopCommand(server)
            waitingThreads[server] = threading.Thread(
                target=waitForServerToStop, args=(server,), daemon=True
            )
            waitingThreads[server].start()
    for server in waitingThreads:
        waitingThreads[server].join()
    exit(0)


signal.signal(signal.SIGTERM, catchSigTerm)


class InvalidCommandException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class SocketHandler(socketserver.BaseRequestHandler):
    def handle(self):
        # logging.info(f"new socket connection from {self.client_address}")

        self.sockIn = self.request.makefile()
        self.active = True
        while self.active:
            cmd = self.sockIn.readline()
            if not cmd:
                break
            logging.info(f"recieved command {cmd}")
            cmdArgs = cmd.split()
            try:
                if cmdArgs[0] == "start":
                    self.startServer(cmdArgs)
                elif cmdArgs[0] == "stop":
                    self.stopServer(cmdArgs)
                elif cmdArgs[0] == "restart":
                    self.restartServer(cmdArgs)
                elif cmdArgs[0] == "status":
                    self.getServerStatus(cmdArgs)
                elif cmdArgs[0] == "console":
                    self.launchServerConsole(cmdArgs)
                elif cmdArgs[0] == "help":
                    self.printHelp(cmdArgs)
                else:
                    raise InvalidCommandException(f"unknown command: {cmdArgs[0]}")
            except InvalidCommandException as e:
                self.request.sendall(str(e).encode() + b"\n")

        # logging.info(f"closed connection from {self.client_address}")

    def printHelp(self, cmdArgs):
        self.request.sendall(
            ("This is the BYU minecraft server controller interface\n" +
            "COMMANDS: \n" +
            "start [serverName]... - starts the specified server(s) (or all if none specified)\n" +
            "stop [serverName]... - stops the specified server(s) (or all if none specified)\n" +
            "restart [serverName]... - restarts the specified server(s) (or all currently online servers if none specified)\n" +
            "status - returns the status of all servers\n" + 
            "console [serverName] - opens the server console of specified server\n" +
            "help - displays this help message\n").encode()
        )

    def startServer(self, cmdArgs):
        serversToStart = []
        if len(cmdArgs) > 1:
            serversToStart = cmdArgs[1:]
        else:
            serversToStart = [x for x in serverStatus if serverStatus[x]['text'] == "OFF"]

        for server in serversToStart:
            if server not in serverStatus:
                raise InvalidCommandException(f"unknown server: {server}")
            if serverStatus[server]['text'] != "OFF":
                raise InvalidCommandException(f"Server {server} already started")
            serverStatus[server]['text'] = "LAUNCHING"
            startNewServer(serverInfoMap[server])
        self.request.sendall(b"started server\n")

    

    def stopServer(self, cmdArgs):
        targetServers = []
        if len(cmdArgs) > 1:
            targetServers = cmdArgs[1:]
        else:
            targetServers = [x for x in serverStatus if serverStatus[x]['text'] == "ON"]
        
        for server in targetServers:
            if server not in serverStatus:
                raise InvalidCommandException(f"unknown server: {server}")
            if serverStatus[server]['text'] == "OFF":
                raise InvalidCommandException(f"Cannot stop Server {server}: server already offline")
            serverStatus[server]['text'] = "STOPPING"
            serverStatus[server]["stopping"] = True
            sendStopCommand(server)
            threading.Thread(
                target=waitForServerToStop, args=(server,), daemon=True
            ).start()
        self.request.sendall(b"stopping server\n")

    def restartServer(self, cmdArgs):
        targetServers = []
        if len(cmdArgs) > 1:
            targetServers = cmdArgs[1:]
        else:
            targetServers = [x for x in serverStatus if serverStatus[x]['text'] == "ON"]

        for server in targetServers:
            if server not in serverStatus:
                raise InvalidCommandException(f"unknown server: {server}")
            serverStatus[server]['text'] = "RESTARTING"
            threading.Thread(
                target=waitForServerToStop, args=(server,), daemon=True
            ).start()
            sendStopCommand(server)
        self.request.sendall(b"Restarting Servers\n")

    def getServerStatus(self, cmdArgs):
        self.request.sendall(json.dumps(serverStatus).encode())

    def launchServerConsole(self, cmdArgs):
        if len(cmdArgs) != 2:
            raise InvalidCommandException(f"unexpect arguments to command")
        server = cmdArgs[1]
        if server not in serverStatus:
            raise InvalidCommandException(f"unknown server: {server}")
        socketListLock[server].acquire()
        openSockets[server].append(self.request)
        socketListLock[server].release()
        self.request.sendall(b"Launching Server Console\n")
        while True:
            line = self.sockIn.readline()
            if not line:
                break
            writeToServer(server, line.encode())
        socketListLock[server].acquire()
        if self.request in openSockets[server]:
            openSockets[server].remove(self.request)
        socketListLock[server].release()


def writeToServer(serverName: str, output: bytes):
    serverInputLock[serverName].acquire()
    try:
        logging.info(f"writing {output} to {serverName}")
        openProcess[serverName].stdin.write(output)
        openProcess[serverName].stdin.flush()
    finally:
        serverInputLock[serverName].release()


def sendToAllListeningSockets(serverName: str, output: bytes):
    for sock in openSockets[serverName]:
        try:
            sock.sendall(output)
        except BrokenPipeError as e:
            socketListLock[serverName].acquire()
            if sock in openSockets[serverName]:
                openSockets[serverName].remove(sock)
            socketListLock[serverName].release()


def runSocketServer():
    global socketServer
    if os.path.exists(port):
        os.unlink(port)
    with socketserver.ThreadingUnixStreamServer(port, SocketHandler) as socketServer:
        atexit.register(closeSocketServer, port)
        socketServer.serve_forever()


def closeSocketServer(serverPort):
    socketServer.shutdown()
    os.unlink(serverPort)


def startNewServer(server: serverConfig.ServerConfig, delay=0):
    serverThreads[server.name] = threading.Thread(
        target=launchServer, args=(server,delay), daemon=True
    )
    serverThreads[server.name].start()


def sendStopCommand(serverName: str):
    serverinfo = serverInfoMap[serverName]
    writeToServer(serverName, (serverinfo.stopCmd + "\n").encode())

def waitForServerToStop(serverName):
        logging.info(f"waiting for server {serverName} to stop")
        proccess = openProcess[serverName]
        try:
            proccess.wait(timeout=shutdownWaitTimeSeconds)
            return
        except subprocess.TimeoutExpired:
            logging.error(f"Timeout occured on stop server {serverName}")
        if proccess.poll() == None:
            serverStatus[serverName]['text'] = "Terminating"
            logging.error(f"{serverName} sending terminate signal")
            proccess.terminate()
        try:
            proccess.wait(timeout=killWaitTimeSeconds)
            return
        except subprocess.TimeoutExpired:
            logging.error(f"Timeout occured on kill server {serverName}")
        if proccess.poll() == None:
            serverStatus[serverName]['text'] = "Killing"
            logging.error(f"{serverName} sending terminate signal")
            proccess.kill()

def waitForServerStart(serverName: str):
    time.sleep(startUpWaitTime)
    if not serverStatus[serverName]["text"] == "STARTING":
        return # all is well
    logging.error(f"{serverName} failed to start")
    proccess = openProcess[serverName]
    if proccess and proccess.poll() == None:
            serverStatus[serverName]['text'] = "Terminating"
            logging.error(f"{serverName} sending terminate signal")
            proccess.terminate()
    try:
        proccess.wait(timeout=killWaitTimeSeconds)
        return
    except subprocess.TimeoutExpired:
        logging.error(f"Timeout occured on kill server {serverName}")
    if proccess and proccess.poll() == None:
        serverStatus[serverName]['text'] = "Killing"
        logging.error(f"{serverName} sending terminate signal")
        proccess.kill()

def launchServer(serverInfo: serverConfig.ServerConfig, delay=0):
    time.sleep(delay)
    while True:
        logging.info(f"launching server: {serverInfo.name}")
        with subprocess.Popen(
            shlex.split(serverInfo.launchCmd),
            cwd=serverInfo.folder,
            text=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            stdin=subprocess.PIPE,
        ) as proc:
            openProcess[serverInfo.name] = proc
            serverStatus[serverInfo.name]["text"] = "STARTING"
            serverStatus[server.name]["stopping"] = False
            startTimeoutThread = threading.Thread(
                target=waitForServerStart, args=(serverInfo.name,), daemon=True
            )
            startTimeoutThread.start()
            # os.set_blocking(proc.stdout.fileno(), False)
            while proc.poll() == None:
                try:
                    readline = proc.stdout.readline()
                    logging.debug(f"{serverInfo.name}: {readline}")
                    if(serverStatus[serverInfo.name]["text"] == "STARTING"):
                        if re.match(serverInfo.startedLine, readline.decode()):
                            serverStatus[serverInfo]["text"] = "ON"

                    sendToAllListeningSockets(serverInfo.name, readline)
                except Exception as e:
                    print(f"recieved exception {serverInfo.name} io: {str(e)}")
            retCode = proc.poll()
            print(f"{serverInfo.name} ended with return code {retCode}")
            openProcess[serverInfo.name] = None
            sendToAllListeningSockets(
                serverInfo.name,
                f"{serverInfo.name} stopped with exit code {retCode}\n".encode(),
            )
            if (
                serverStatus[serverInfo.name]["stopping"]
            ):  # don't restart if shutting down was intentional
                serverStatus[serverInfo.name]["text"] = "OFF"
                serverStatus[serverInfo.name]["stopping"] = False
                break
            serverStatus[serverInfo.name]["text"] = "OFF"


logging.basicConfig(level=logging.DEBUG)

serverInfoList = serverConfig.getServerConfigs("servers.json")
serverInfoMap: "dict[str:serverConfig.ServerConfig]" = dict()
i = 0
for server in serverInfoList:
    socketListLock[server.name] = threading.Lock()
    serverInputLock[server.name] = threading.Lock()
    openSockets[server.name] = []
    serverInfoMap[server.name] = server
    serverStatus[server.name] = {}
    serverStatus[server.name]["text"] = "OFF"
    serverStatus[server.name]["stopping"] = False
    if server.start:
        startNewServer(server, startUpDelaySeconds*i)
        i +=1
        
runSocketServer()
