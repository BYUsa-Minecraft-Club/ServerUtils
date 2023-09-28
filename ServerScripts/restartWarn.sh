#!/bin/bash
echo "hello world"
/usr/bin/date > /tmp/restartwarnLog
python3 -V
/usr/bin/python3 /home/garrett/Downloads/testSever/warnOfRestart.py &> /tmp/pythonErrors || echo "failed"
echo "finished"
