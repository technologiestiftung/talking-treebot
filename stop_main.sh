#!/bin/bash
if [ -f main_pid.txt ]; then
    PID=$(cat main_pid.txt)
    echo "Stopping main.py with PID $PID"
    kill $PID
    rm main_pid.txt  # Clean up the PID file
else
    echo "No running main.py script found"
fi