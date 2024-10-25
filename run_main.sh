#!/bin/bash
echo "Starting main.py..."
source /home/talkingtreebot/talking-treebot/treebot-env/bin/activate
sleep 1.5
python /home/talkingtreebot/talking-treebot/main.py &
echo $! > main_pid.txt  # Store the PID of the Python script
echo "main.py script finished"