#!/bin/bash
echo "Starting main.py..."
source /home/treebot/talking-treebot/treebot-env/bin/activate
python /home/treebot/talking-treebot/main.py &
echo $! > main_pid.txt  # Store the PID of the Python script
echo "main.py script finished"
