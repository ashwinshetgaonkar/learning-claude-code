# Combined Dockerfile for GCP Cloud Run
# Builds both frontend and backend in a single container

# Stage 1: Build frontend
FROM node:20-alpine AS frontend-builder
WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# Stage 2: Final image with Python backend + nginx
FROM python:3.11-slim

# Install nginx and supervisor
RUN apt-get update && apt-get install -y --no-install-recommends \
    nginx \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/app/ ./app/

# Copy frontend build
COPY --from=frontend-builder /frontend/dist /usr/share/nginx/html

# Copy nginx config for Cloud Run (single port)
RUN rm /etc/nginx/sites-enabled/default
COPY <<'EOF' /etc/nginx/conf.d/default.conf
server {
    listen 8080;
    server_name localhost;
    root /usr/share/nginx/html;
    index index.html;

    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml text/javascript;

    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location / {
        try_files $uri $uri/ /index.html;
    }

    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
EOF

# Startup script to run both services
COPY <<'EOF' /app/start.sh
#!/bin/bash
set -e

echo "Starting AI News Tracker..."
echo "DATABASE_URL: $DATABASE_URL"
echo "CORS_ORIGINS: $CORS_ORIGINS"

# Start nginx in background
nginx -g "daemon off;" &
NGINX_PID=$!

# Start backend
cd /app
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --log-level info
EOF
RUN chmod +x /app/start.sh

# Supervisor config to run both nginx and uvicorn
COPY <<'EOF' /etc/supervisor/conf.d/supervisord.conf
[supervisord]
nodaemon=true
user=root
loglevel=debug

[program:nginx]
command=nginx -g "daemon off;"
autostart=true
autorestart=true
stdout_logfile=/dev/stdout
stdout_logfile_maxbytes=0
stderr_logfile=/dev/stderr
stderr_logfile_maxbytes=0

[program:backend]
command=uvicorn app.main:app --host 0.0.0.0 --port 8000 --log-level info
directory=/app
autostart=true
autorestart=unexpected
startretries=3
stdout_logfile=/dev/stdout
stdout_logfile_maxbytes=0
stderr_logfile=/dev/stderr
stderr_logfile_maxbytes=0
environment=PYTHONUNBUFFERED="1"
EOF

# Create data directory for SQLite (in /app where backend runs)
RUN mkdir -p /app/data

ENV DATABASE_URL=sqlite+aiosqlite:////app/data/ai_news.db
ENV CORS_ORIGINS=*
ENV PORT=8080

EXPOSE 8080

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
