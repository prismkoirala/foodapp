# Production Deployment Guide

This guide covers deploying the Food Ordering Platform to production.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Backend Deployment](#backend-deployment)
3. [Frontend Deployment](#frontend-deployment)
4. [Database Setup](#database-setup)
5. [Environment Variables](#environment-variables)
6. [SSL/HTTPS](#sslhttps)
7. [Monitoring](#monitoring)

---

## Prerequisites

### Required Software
- Python 3.10+
- PostgreSQL 14+
- Node.js 18+
- Nginx
- Redis (optional, for caching)
- Certbot (for SSL)

### Recommended Services
- AWS/DigitalOcean/Heroku for hosting
- AWS S3/Cloudinary for media storage
- Sentry for error tracking
- SendGrid/Mailgun for emails

---

## Backend Deployment

### 1. Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install python3-pip python3-venv nginx postgresql redis-server -y

# Create project directory
sudo mkdir -p /var/www/foodapp
sudo chown $USER:$USER /var/www/foodapp
cd /var/www/foodapp
```

### 2. Clone and Setup Project

```bash
# Clone repository
git clone <your-repo-url> .

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install gunicorn psycopg2-binary
```

### 3. Environment Configuration

Create `/var/www/foodapp/.env.production`:

```env
# Django Settings
DJANGO_ENV=production
SECRET_KEY=<generate-strong-secret-key>
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database
DB_NAME=foodapp_prod
DB_USER=foodapp_user
DB_PASSWORD=<strong-database-password>
DB_HOST=localhost
DB_PORT=5432

# CORS
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Media/Static Files
STATIC_ROOT=/var/www/foodapp/staticfiles
MEDIA_ROOT=/var/www/foodapp/media
STATIC_URL=/static/
MEDIA_URL=/media/

# Email (SendGrid example)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=<sendgrid-api-key>
DEFAULT_FROM_EMAIL=noreply@yourdomain.com

# Security
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True

# Optional: AWS S3 for Media
USE_S3=True
AWS_ACCESS_KEY_ID=<your-access-key>
AWS_SECRET_ACCESS_KEY=<your-secret-key>
AWS_STORAGE_BUCKET_NAME=<your-bucket-name>
AWS_S3_REGION_NAME=us-east-1
```

### 4. Database Setup

```bash
# Create PostgreSQL database and user
sudo -u postgres psql

CREATE DATABASE foodapp_prod;
CREATE USER foodapp_user WITH PASSWORD 'your-strong-password';
ALTER ROLE foodapp_user SET client_encoding TO 'utf8';
ALTER ROLE foodapp_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE foodapp_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE foodapp_prod TO foodapp_user;
\q
```

### 5. Run Migrations and Collect Static

```bash
# Set environment
export DJANGO_ENV=production

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --noinput

# Load test data (optional)
python setup_test_data.py
```

### 6. Gunicorn Configuration

Create `/var/www/foodapp/gunicorn_config.py`:

```python
bind = "127.0.0.1:8000"
workers = 4
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2
errorlog = "/var/log/gunicorn/error.log"
accesslog = "/var/log/gunicorn/access.log"
loglevel = "info"
```

Create log directory:
```bash
sudo mkdir -p /var/log/gunicorn
sudo chown $USER:$USER /var/log/gunicorn
```

### 7. Systemd Service

Create `/etc/systemd/system/foodapp.service`:

```ini
[Unit]
Description=Food Ordering Platform Gunicorn Daemon
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/foodapp
Environment="DJANGO_ENV=production"
ExecStart=/var/www/foodapp/venv/bin/gunicorn \
    --config /var/www/foodapp/gunicorn_config.py \
    foodapp_backend.wsgi:application

[Install]
WantedBy=multi-user.target
```

Enable and start service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable foodapp
sudo systemctl start foodapp
sudo systemctl status foodapp
```

### 8. Nginx Configuration

Create `/etc/nginx/sites-available/foodapp`:

```nginx
# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

# HTTPS Server
server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Client Max Body Size (for file uploads)
    client_max_body_size 10M;

    # Static Files
    location /static/ {
        alias /var/www/foodapp/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Media Files
    location /media/ {
        alias /var/www/foodapp/media/;
        expires 7d;
        add_header Cache-Control "public";
    }

    # API Backend
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Admin
    location /admin/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Frontend Apps (React builds)
    location / {
        root /var/www/foodapp/frontend/dist/customer-app;
        try_files $uri /index.html;
    }

    location /manager/ {
        alias /var/www/foodapp/frontend/dist/manager-portal/;
        try_files $uri /index.html;
    }

    location /kitchen/ {
        alias /var/www/foodapp/frontend/dist/kitchen-display/;
        try_files $uri /index.html;
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/foodapp /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## Frontend Deployment

### 1. Build All Apps

```bash
cd /var/www/foodapp/frontend

# Customer App
cd apps/customer-app
npm install --production
npm run build

# Manager Portal
cd ../manager-portal
npm install --production
npm run build

# Kitchen Display
cd ../kitchen-display
npm install --production
npm run build
```

### 2. Production Environment Variables

Create production `.env.production` files for each app:

**Customer App:**
```env
VITE_API_URL=https://yourdomain.com/api/v1
```

**Manager Portal:**
```env
VITE_API_URL=https://yourdomain.com/api/v1
```

**Kitchen Display:**
```env
VITE_API_URL=https://yourdomain.com/api/v1
```

### 3. Update Build Scripts

Add to each app's `package.json`:

```json
{
  "scripts": {
    "build:prod": "vite build --mode production"
  }
}
```

---

## SSL/HTTPS Setup

### Using Let's Encrypt (Free)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Obtain SSL Certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal (already configured by certbot)
sudo certbot renew --dry-run
```

---

## Database Backup

### Automated Daily Backups

Create `/usr/local/bin/backup-database.sh`:

```bash
#!/bin/bash
BACKUP_DIR="/var/backups/foodapp"
DATE=$(date +%Y%m%d_%H%M%S)
FILENAME="foodapp_backup_$DATE.sql"

mkdir -p $BACKUP_DIR

pg_dump -U foodapp_user foodapp_prod > $BACKUP_DIR/$FILENAME

# Compress
gzip $BACKUP_DIR/$FILENAME

# Keep only last 30 days
find $BACKUP_DIR -name "*.gz" -mtime +30 -delete

echo "Backup completed: $FILENAME.gz"
```

Make executable and add to cron:
```bash
sudo chmod +x /usr/local/bin/backup-database.sh
sudo crontab -e

# Add this line (daily at 2 AM):
0 2 * * * /usr/local/bin/backup-database.sh
```

---

## Monitoring

### 1. Logs

```bash
# Gunicorn logs
tail -f /var/log/gunicorn/error.log
tail -f /var/log/gunicorn/access.log

# Nginx logs
tail -f /var/nginx/access.log
tail -f /var/nginx/error.log

# Django logs
tail -f /var/www/foodapp/logs/django.log
```

### 2. Sentry Integration

Install Sentry SDK:
```bash
pip install sentry-sdk
```

Add to `foodapp_backend/settings/production.py`:
```python
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn="<your-sentry-dsn>",
    integrations=[DjangoIntegration()],
    traces_sample_rate=0.1,
    send_default_pii=True,
    environment="production",
)
```

### 3. Health Checks

Create `/var/www/foodapp/healthcheck.sh`:
```bash
#!/bin/bash
curl -f http://localhost:8000/api/v1/ || exit 1
```

---

## Performance Optimization

### 1. Redis Caching (Optional)

Install Redis:
```bash
sudo apt install redis-server -y
pip install django-redis
```

Add to settings:
```python
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}
```

### 2. Database Optimization

```sql
-- Add indexes
CREATE INDEX idx_orders_status ON orders_order(status);
CREATE INDEX idx_orders_restaurant ON orders_order(restaurant_id);
CREATE INDEX idx_orders_created ON orders_order(created_at);
```

### 3. CDN for Static Files

- Use Cloudflare or AWS CloudFront
- Configure in Django settings
- Update STATIC_URL to CDN URL

---

## Scaling

### Horizontal Scaling

1. **Load Balancer** - Use Nginx or AWS ALB
2. **Multiple App Servers** - Run multiple Gunicorn instances
3. **Database Replication** - PostgreSQL read replicas
4. **Redis Cluster** - For distributed caching

### Vertical Scaling

- Increase Gunicorn workers based on CPU cores
- Increase database connection pool
- Increase server resources (RAM, CPU)

---

## Security Checklist

- [ ] Change DEBUG to False
- [ ] Use strong SECRET_KEY
- [ ] Configure ALLOWED_HOSTS
- [ ] Enable SSL/HTTPS
- [ ] Set secure cookie flags
- [ ] Configure CORS properly
- [ ] Use environment variables for secrets
- [ ] Regular security updates
- [ ] Database backups
- [ ] Rate limiting (Django Ratelimit)
- [ ] WAF (Cloudflare, AWS WAF)

---

## Rollback Procedure

If deployment fails:

```bash
# 1. Stop new version
sudo systemctl stop foodapp

# 2. Restore database backup
gunzip /var/backups/foodapp/foodapp_backup_YYYYMMDD_HHMMSS.sql.gz
psql -U foodapp_user foodapp_prod < foodapp_backup_YYYYMMDD_HHMMSS.sql

# 3. Checkout previous version
git checkout <previous-commit-hash>

# 4. Restart service
sudo systemctl start foodapp
```

---

## Support

For deployment issues:
- Check logs in `/var/log/gunicorn/`
- Check Nginx logs in `/var/log/nginx/`
- Verify database connectivity
- Check firewall settings
- Verify SSL certificates

---

**Production Deployment Checklist:**
1. ✅ Environment variables configured
2. ✅ Database created and migrated
3. ✅ Static files collected
4. ✅ Gunicorn service running
5. ✅ Nginx configured
6. ✅ SSL certificate installed
7. ✅ Firewall configured
8. ✅ Backups scheduled
9. ✅ Monitoring set up
10. ✅ DNS configured
