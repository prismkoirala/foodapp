# Multi-stage build for Django backend

FROM python:3.11-slim as backend

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_ENV=production

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir gunicorn psycopg2-binary

# Copy project files
COPY . /app/

# Collect static files
RUN python manage.py collectstatic --noinput

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Run gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "foodapp_backend.wsgi:application"]
