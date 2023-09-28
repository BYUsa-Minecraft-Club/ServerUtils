#!/bin/python3
import os
import sys

output = os.open("serverOutput", os.O_RDONLY)
print("Server Console Opened")
if os.fork() == 0:
    input = os.open("serverInput",os.O_WRONLY)
    while(True):
        datain =os.read(1, 1)
        os.write(input, datain)
else:
    while(True):
        os.write(2, os.read(output, 1))

