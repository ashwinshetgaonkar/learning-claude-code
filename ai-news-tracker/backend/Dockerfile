FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/

# Create directory for SQLite database
RUN mkdir -p /data

# Set environment variables
ENV DATABASE_URL=sqlite+aiosqlite:///./data/ai_news.db
ENV PORT=8080

# Expose port
EXPOSE 8080

# Run the application
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
