#!/bin/bash
# restart.sh - Script to restart all Thinking platform services
# Created: April 2025

# Set colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Print header
echo -e "${GREEN}=== Thinking Platform Service Restart ===${NC}"
echo "Started at: $(date)"
echo

# Function to restart a service
restart_service() {
    local service_name=$1
    echo -e "${YELLOW}Restarting $service_name...${NC}"
    
    if sudo systemctl restart $service_name; then
        echo -e "${GREEN}✓ Successfully restarted $service_name${NC}"
    else
        echo -e "${RED}✗ Failed to restart $service_name${NC}"
        echo "Check logs with: sudo journalctl -u $service_name -n 50"
        return 1
    fi
    
    # Check service status
    echo "Current status:"
    sudo systemctl status $service_name --no-pager | head -n 5
    echo
    
    return 0
}

# Function to reload a service
reload_service() {
    local service_name=$1
    echo -e "${YELLOW}Reloading $service_name...${NC}"
    
    if sudo systemctl reload $service_name; then
        echo -e "${GREEN}✓ Successfully reloaded $service_name${NC}"
    else
        echo -e "${RED}✗ Failed to reload $service_name. Attempting restart...${NC}"
        restart_service $service_name
    fi
    
    echo
    
    return 0
}

# Restart backend service
restart_service thinking-backend

# Reload Nginx
reload_service nginx

# Print summary
echo -e "${GREEN}=== Restart Complete ===${NC}"
echo "Finished at: $(date)"
echo
echo "If you encounter any issues:"
echo "1. Check backend logs: sudo journalctl -u thinking-backend -f"
echo "2. Check Nginx logs: sudo tail -f /var/log/nginx/error.log"
echo "3. Check application logs: ls -la /home/thinking/logs/"
