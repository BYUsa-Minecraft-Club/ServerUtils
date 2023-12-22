#!/bin/python3
import tkinter as tk
import os
import subprocess
import utils.serverConfig as servers
import socket
import json
import threading
serverList = []
buttonColor = "#7f8280"
backgroundColor = "#444745"
buttonWidth = 10
buttonHeight = 2
port = "/tmp/server.socket"

serverStatus = None

def sendCommandToServer(cmd: str):
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.connect(port)
    sock.sendall(cmd.encode())
    result = sock.recv(2048) # todo handle this better
    sock.close()
    return result

def getServerStatus():
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.connect(port)
    sock.sendall("status\n".encode())
    print("reading in status")
    data = sock.recv(2048)
    result = json.loads(data)
    print(f"got status{result}\n")
    sock.close()
    return result


class Server:
    def __init__(self, serverConfig:servers.ServerConfig) -> None:
       self.serverConfig = serverConfig

    def setupServerUI(self, root):
        print("building server UI")
        mainFrame = tk.Frame(root, bg=backgroundColor)
        
        serverName = tk.Label(mainFrame, text=self.serverConfig.displayName, bg=backgroundColor,fg="white",)
        serverName.pack(side="top")
    
        serverStatusFrame = tk.Frame(mainFrame, bg=backgroundColor)
        serverStatusCaptionLabel = tk.Label(serverStatusFrame, text="Server Status:", bg=backgroundColor,fg="white",)
        self.serverStatusLabel = tk.Label(serverStatusFrame, text="", bg=backgroundColor,fg="white",)
        serverStatusCaptionLabel.pack(side="left")
        self.serverStatusLabel.pack(side="left")
        serverStatusFrame.pack(side="top")

        buttonRow1 = tk.Frame(mainFrame, bg=backgroundColor)
        buttonStartServer = tk.Button(buttonRow1, text="Start Server", width=buttonWidth, height=buttonHeight, bg=buttonColor, fg="white", command=lambda: self.startServer())
        buttonStartServer.pack(side="left")
        buttonStopServer = tk.Button(buttonRow1, text="Stop Server", width=buttonWidth, height=buttonHeight, bg=buttonColor, fg="white", command=lambda: self.stopServer())
        buttonStopServer.pack(side="left")
        buttonRow1.pack(side="top")

        buttonRow2 = tk.Frame(mainFrame, bg=backgroundColor)
        buttonRestartServer = tk.Button(buttonRow2, text="Restart Server", width=buttonWidth, height=buttonHeight, bg=buttonColor, fg="white", command=lambda: self.restartServer())
        buttonOpenServerConsole = tk.Button(buttonRow2, text="Server Console", width=buttonWidth, height=buttonHeight, bg=buttonColor, fg="white", command=lambda: self.launchServerConsole())
        buttonRestartServer.pack(side="left")
        buttonOpenServerConsole.pack(side="left")
        buttonRow2.pack(side="top")
        mainFrame.pack(side="left")

    def updateStatus(self, serverStatus):
       # output = os.popen(f"systemctl status {self.serviceName}")
        # if(output.read().find("active (running)") > 0):
        self.serverStatusLabel.configure(text=serverStatus[self.serverConfig.name])
        # else:
        #  serverStatusLabel.configure(text="Server Status: Off")
        print(f"updating server status {self.serverConfig.displayName}")

    def startServer(self):
        print(f"Starting Server {self.serverConfig.displayName}")
        self.serverStatusLabel.configure(text="Server Starting")
        result = sendCommandToServer(f"start {self.serverConfig.name}\n")
        print(result)
        print("Started Server")

    def stopServer(self):
        print(f"Stopping Server {self.serverConfig.displayName}")
        self.serverStatusLabel.configure(text="Stoping Server")
        result = sendCommandToServer(f"stop {self.serverConfig.name}\n")
        print(result)
        print("Stopped Server")

    def restartServer(self):
        print(f"Restarting Server {self.serverConfig.displayName}")
        self.serverStatusLabel.configure(text="Restarting Server")
        result = sendCommandToServer(f"restart {self.serverConfig.name}\n")
        print(result)
        print("Restarted Server")
    
    def launchServerConsole(self):
        subprocess.call(['gnome-terminal', '--', '/home/resolute/ServerUtils/ServerScripts/terminal.py', "--server", self.serverConfig.name], cwd='/home/resolute/ServerUtils')

    

class ServerWrapperServer(Server):
    def __init__(self, servicename) -> None:
        super().__init__(servers.ServerConfig("ServerWrapper", "Server Wrapper", None, None, None, None))
        self.serviceName = servicename

    def updateStatus(self, serverStatus):
        output = os.popen(f"systemctl status {self.serviceName}")
        if(output.read().find("active (running)") > 0):
            self.serverStatusLabel.configure(text="On", fg="green")
        else:
            self.serverStatusLabel.configure(text="On", fg="red")
        print(f"updating server status {self.serverConfig.displayName}")

    def startServer(self):
        print(f"Starting Server {self.serverConfig.displayName}")
        os.system(f'sudo systemctl start {self.serviceName}')
        self.serverStatusLabel.configure(text="Server Starting")
        print("Started Server")

    def stopServer(self):
        print(f"Stopping Server {self.serverConfig.displayName}")
        os.system(f'sudo systemctl stop {self.serviceName}')
        self.serverStatusLabel.configure(text="Stoping Server")
        print("Stopped Server")

    def restartServer(self):
        print(f"Restarting Server {self.serverConfig.displayName}")
        os.system(f'systemctl restart {self.serviceName}')
        self.serverStatusLabel.configure(text="Restarting Server")
        print("Restarted Server")

def updatePeriodic(window):
    serverStatus = getServerStatus()
    for server in serverList:
        server.updateStatus(serverStatus)
    window.after(1000, updatePeriodic, window)


def main():
    serverConfigs = servers.getServerConfigs("servers.json")
    window = tk.Tk()
    window.configure(background=backgroundColor)
    greeting = tk.Label(window, text="Welcome Admins",background=backgroundColor, fg="white", font=34, height=2)
    greeting.pack()
    print(serverConfigs)

    
    index = 0
    frame = tk.Frame(window,background=backgroundColor)
    frame.pack(side="top")
    serverWrapperServer = ServerWrapperServer("minecraft.service")
    serverWrapperServer.setupServerUI(frame)
    serverList.append(serverWrapperServer)
    frame = tk.Frame(window,background=backgroundColor)
    frame.pack(side="top")
    for serverConfig in serverConfigs:
        server = Server(serverConfig)
        server.setupServerUI(frame)
        serverList.append(server)
        index +=1
        if(index%2 == 0):
            frame = tk.Frame(window, background=backgroundColor)
            frame.pack(side="top")

    window.after(1000, updatePeriodic, window)
    window.mainloop()

if __name__ == "__main__":
    main()