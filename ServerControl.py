#!/bin/python3
import tkinter as tk
import os
import subprocess

def startServer():
   print("Starting Server")
   serverStatusLabel.configure(text="Server Starting")
   os.system('sudo systemctl start minecraft.service')
   print("Started Server")

def stopServer():
    print("Stopping Server")
    serverStatusLabel.configure(text="Stoping Server")
    os.system('sudo systemctl stop minecraft.service')
    print("Stopped Server")

def restartServer():
    print("Restarting Server")
    serverStatusLabel.configure(text="Restarting Server")
    os.system('sudo systemctl restart minecraft.service')
    print("Restarted Server")
    
def launchServerConsole():
    subprocess.call(['gnome-terminal', '--title="Server Console"', '--', '/home/byumc/ServerUtils/ServerScripts/terminal.py'], cwd='/home/byumc/ServerUtils/ServerScripts')

def updatePeriodic():
	output = os.popen("systemctl status minecraft.service")
	if(output.read().find("active (running)") > 0):
		serverStatusLabel.configure(text="Server Status: On")
	else:
	 serverStatusLabel.configure(text="Server Status: Off")
	window.after(1000, updatePeriodic)


window = tk.Tk()
greeting = tk.Label(text="Greetings, Admin!")
greeting.pack()
serverStatusLabel = tk.Label(text="Server Status: ")
serverStatusLabel.pack()
buttonStartServer = tk.Button(text="Start Server", width=25, height=5, bg="blue", fg="yellow", command=startServer)
buttonStopServer = tk.Button(text="Stop Server", width=25, height=5, bg="blue", fg="yellow", command=stopServer)
buttonRestartServer = tk.Button(text="Restart Server", width=25, height=5, bg="blue", fg="yellow", command=restartServer)
buttonOpenServerConsole = tk.Button(text="Server Console", width=25, height=5, bg="blue", fg="yellow", command=launchServerConsole)
buttonStartServer.pack()
buttonStopServer.pack()
buttonRestartServer.pack()
buttonOpenServerConsole.pack()
window.after(1000, updatePeriodic)
window.mainloop()
