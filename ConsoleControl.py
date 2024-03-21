#!/bin/python3
import os
import subprocess
import utils.serverConfig as servers
import socket
import argparse
import json
port = "/tmp/server.socket"

serverConfigs = servers.getServerConfigs("servers.json")

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


def main():
    parser = argparse.ArgumentParser(prog="ConsolControl")
    parser.add_argument("operation", type=str, choices=["start", "stop", "restart", "status", "console"], nargs=1,)
    parser.add_argument("server", type=str, choices=[x.name for x in serverConfigs]+["wrapper",""], nargs='*',default="")
    args = parser.parse_args()
    operation = args.operation[0]
    if  "wrapper" in args.server:
        if operation == "status":
            output = os.popen(f"systemctl status minecraft.service")
            if(output.read().find("active (running)") > 0):
                print("wrapper: ON")
            else:
                 print("wrapper: OFF")
        elif operation == "start":
            os.system(f'sudo systemctl start minecraft.service')
            print("Started Server")
        elif operation == "stop":
            os.system(f'sudo systemctl stop minecraft.service')
            print("Stopped Server")
        elif operation == "restart":
            os.system(f'systemctl restart minecraft.service')
            print("Restarted Server")
        elif operation == "console":
            os.system("/home/byumc/BYU_Servers/ServerControlScripts/ServerScripts/terminal.py")
    elif not os.path.exists(port):
       print("server wrapper offline cannot execute command")
       print("Run `./ConsoleControl.py start wrapper` to start wrapper")
       exit(-1)
    elif operation == "status":
        status = getServerStatus()
        if args.server:
            for server in args.server:
                print(f"{server}: {status[server]}")
        else:
            for server in status:
                print(f"{server}: {status[server]}")
    elif operation == "console":
        if len(args.server) > 1:
            print("can only open terminal for one server at a time\n")
            exit(-1)
        if args.server:
            os.system("/home/byumc/BYU_Servers/ServerControlScripts/ServerScripts/terminal.py"+ " -s "+ args.server[0])
        else:
            os.system("/home/byumc/BYU_Servers/ServerControlScripts/ServerScripts/terminal.py")
    else:
        if args.server:
           cmd = operation + " " + " ".join(args.server) + "\n"
        else:
           cmd = operation + "\n"
        result = sendCommandToServer(cmd)
        print(result.decode())

if __name__ == "__main__":
    main()
