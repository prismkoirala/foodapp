#!/bin/bash
# Production Deployment Script

set -e  # Exit on error

echo "====================================="
echo "Food Ordering Platform - Deployment"
echo "====================================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_DIR="/var/www/foodapp"
VENV_DIR="$PROJECT_DIR/venv"
DJANGO_ENV="production"

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   echo -e "${RED}ERROR: Do not run this script as root${NC}"
   exit 1
fi

echo -e "${YELLOW}Step 1: Pulling latest code from Git...${NC}"
cd $PROJECT_DIR
git pull origin main

echo -e "${YELLOW}Step 2: Activating virtual environment...${NC}"
source $VENV_DIR/bin/activate

echo -e "${YELLOW}Step 3: Installing/updating dependencies...${NC}"
pip install -r requirements-production.txt --upgrade

echo -e "${YELLOW}Step 4: Running database migrations...${NC}"
export DJANGO_ENV=$DJANGO_ENV
python manage.py migrate --noinput

echo -e "${YELLOW}Step 5: Collecting static files...${NC}"
python manage.py collectstatic --noinput

echo -e "${YELLOW}Step 6: Running tests (optional)...${NC}"
# python manage.py test --keepdb || echo "Tests failed but continuing..."

echo -e "${YELLOW}Step 7: Restarting Gunicorn service...${NC}"
sudo systemctl restart foodapp

echo -e "${YELLOW}Step 8: Checking service status...${NC}"
sudo systemctl status foodapp --no-pager

echo -e "${YELLOW}Step 9: Reloading Nginx...${NC}"
sudo nginx -t && sudo systemctl reload nginx

echo -e "${GREEN}✓ Deployment completed successfully!${NC}"
echo ""
echo "Useful commands:"
echo "  - View logs: sudo journalctl -u foodapp -f"
echo "  - Check status: sudo systemctl status foodapp"
echo "  - Restart service: sudo systemctl restart foodapp"
echo ""
