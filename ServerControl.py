#!/bin/python3
import tkinter as tk
import os
import subprocess
import utils.serverConfig as servers

serverList = []
buttonColor = "#7f8280"
backgroundColor = "#444745"
buttonWidth = 10
buttonHeight = 2
class Server:
    def __init__(self, serverConfig:servers.ServerConfig) -> None:
       self.serverConfig = serverConfig
       self.serviceName = serverConfig.name+".service"

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
        buttonStartServer = tk.Button(buttonRow1, text="Start Server", width=buttonWidth, height=buttonHeight, bg=buttonColor, fg="white", command=lambda: startServer(self))
        buttonStartServer.pack(side="left")
        buttonStopServer = tk.Button(buttonRow1, text="Stop Server", width=buttonWidth, height=buttonHeight, bg=buttonColor, fg="white", command=lambda: stopServer(self))
        buttonStopServer.pack(side="left")
        buttonRow1.pack(side="top")

        buttonRow2 = tk.Frame(mainFrame, bg=backgroundColor)
        buttonRestartServer = tk.Button(buttonRow2, text="Restart Server", width=buttonWidth, height=buttonHeight, bg=buttonColor, fg="white", command=lambda: restartServer(self))
        buttonOpenServerConsole = tk.Button(buttonRow2, text="Server Console", width=buttonWidth, height=buttonHeight, bg=buttonColor, fg="white", command=lambda: launchServerConsole(self))
        buttonRestartServer.pack(side="left")
        buttonOpenServerConsole.pack(side="left")
        buttonRow2.pack(side="top")
        mainFrame.pack(side="left")

    def updateStatus(self):
       # output = os.popen(f"systemctl status {self.serviceName}")
        # if(output.read().find("active (running)") > 0):
        self.serverStatusLabel.configure(text="On", fg="green")
        # else:
        #  serverStatusLabel.configure(text="Server Status: Off")
        print(f"updating server status {self.serverConfig.displayName}")

def startServer(server):
   print(f"Starting Server {server.serverConfig.displayName}")
   os.system(f'sudo systemctl start {server.serviceName}.service')
   server.serverStatusLabel.configure(text="Server Starting")
   print("Started Server")

def stopServer(server):
    print(f"Stopping Server {server.serverConfig.displayName}")
    os.system(f'sudo systemctl stop {server.serviceName}.service')
    server.serverStatusLabel.configure(text="Stoping Server")
    print("Stopped Server")

def restartServer(server):
    print(f"Restarting Server {server.serverConfig.displayName}")
    os.system(f'systemctl restart {server.serviceName}.service')
    server.serverStatusLabel.configure(text="Restarting Server")
    print("Restarted Server")
    
def launchServerConsole(server):
    pass
    subprocess.call(['gnome-terminal', '--', '/home/resolute/ServerUtils/ServerScripts/terminal.py', "--server", server.serverConfig.name], cwd='/home/resolute/ServerUtils')

def updatePeriodic(window):
    for server in serverList:
        server.updateStatus()
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