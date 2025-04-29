#!/bin/bash
# Restart the proxy FastAPI service using uvicorn

# Activate virtual environment if needed
#!/bin/bash
# Restart the proxy FastAPI uvicorn service (for use behind Nginx)

PID=$(ps aux | grep 'uvicorn proxy.proxy:app' | grep -v grep | awk '{print $2}')
if [ ! -z "$PID" ]; then
    kill $PID
    sleep 1
fi
nohup uvicorn src.proxy:app --host 127.0.0.1 --port 8000 --proxy-headers > ../proxy.log 2>&1 &
echo "Proxy server restarted. To check logs: tail -f proxy/proxy.log"
