#!/bin/bash
# Start the Hub in background
cd "$(dirname "$0")/.."

echo "Starting Discovery Hub..."
nohup python3 -m src.hub.main > hub.log 2>&1 &
PID=$!
echo "Hub started with PID $PID. Logs in hub.log."
echo $PID > hub.pid
