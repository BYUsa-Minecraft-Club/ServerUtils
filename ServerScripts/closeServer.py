#!/bin/python3
import time
import os

print("stoping server")
input = os.open("serverInput",os.O_WRONLY)
os.write(input, b"/say I'm shutting down now!\r")
time.sleep(10)
os.write(input, b"/stop\r")

output = os.open("serverOutput", os.O_RDONLY)

time.sleep(10)

os.close(input)
os.close(output)



