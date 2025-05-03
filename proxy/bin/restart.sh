#!/bin/bash
# Restart the proxy FastAPI uvicorn service (for use behind Nginx)

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROXY_DIR="$( dirname "$SCRIPT_DIR" )"
VENV_DIR="$PROXY_DIR/../.venv"

# Check if we need to use a local venv instead
if [ ! -d "$VENV_DIR" ] && [ -d "$PROXY_DIR/.venv" ]; then
    VENV_DIR="$PROXY_DIR/.venv"
fi

# Activate virtual environment
source "$VENV_DIR/bin/activate"

# Kill any existing uvicorn process
PID=$(ps aux | grep 'uvicorn.*src.proxy:app' | grep -v grep | awk '{print $2}')
if [ ! -z "$PID" ]; then
    echo "Stopping existing proxy service (PID: $PID)"
    kill $PID
    sleep 1
fi

# Start the service with the full path to uvicorn
echo "Starting proxy service..."
cd "$PROXY_DIR"
"$VENV_DIR/bin/uvicorn" src.proxy:app --host 127.0.0.1 --port 8000 --proxy-headers > "$PROXY_DIR/proxy.log" 2>&1 &

echo "Proxy server restarted. To check logs: tail -f $PROXY_DIR/proxy.log"
