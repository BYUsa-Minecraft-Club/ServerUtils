#!/bin/python3
import time
import os
import re

print("stoping server\n")
input = os.open("serverInput",os.O_WRONLY)
output = os.open("serverOutput", os.O_RDONLY | os.O_NONBLOCK)

minutesToRestart = 5

string = f"/say Server Restarting in {minutesToRestart} minutes\n"
os.write(input, bytes(string, 'utf-8'))

time_end = time.time() + 60* minutesToRestart
prettyOpen = os.fdopen(output)

while time.time() < time_end:
    try:
        line = prettyOpen.readline();
        if "logged in with entity id" in line:
            string = f"/say Server Restarting in {round((time_end-time.time())/60)} minutes\n"
            os.write(input, bytes(string, 'utf-8'))
    except BlockingIOError:
        line = b""





os.write(input, b"/kick @a Server Daily Restart\n")

os.close(input)
os.close(output)
# this script doesn't actually stop the server. It 


