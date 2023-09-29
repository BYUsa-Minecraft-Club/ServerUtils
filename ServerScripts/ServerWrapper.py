#!/bin/python3
import time
import os
import subprocess
with subprocess.Popen(["<SERVER Path>/launchServer.sh"],text=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin = subprocess.PIPE, cwd="<Server Path>") as proc:
    os.set_blocking(proc.stdout.fileno(), False)
    input = os.open("serverInput",os.O_RDONLY | os.O_NONBLOCK)
    try:
       output = os.open("serverOutput", os.O_WRONLY | os.O_NONBLOCK)
    except OSError:
       output = None
    while proc.poll() == None:
        try:
            line = os.read(input,1)
        except BlockingIOError:
            line = b""
        if len(line) != 0:
            proc.stdin.write(line)
            proc.stdin.flush()
        
        readline = proc.stdout.readline()
        try:
            if output == None:
               output = os.open("testOut", os.O_WRONLY | os.O_NONBLOCK)
            os.write(output, readline)
        except OSError:
            if output != None:
              output == None
    retCode = proc.poll()
    exit(retCode) 
