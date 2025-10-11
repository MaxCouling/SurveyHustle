FROM python:3.11-slim

# Install Node.js
RUN apt-get update && apt-get install -y \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy package files
COPY package*.json ./
COPY requirements.txt ./

# Install Node dependencies
RUN npm install

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Build Tailwind CSS
RUN npx tailwindcss -i ./app/static/css/tailwind.css -o ./app/static/css/output.css --minify

# Initialize database (will be replaced by volume mount)
RUN mkdir -p /data

# Expose port
EXPOSE 5000

# Create startup script
COPY <<'EOF' /app/start.sh
#!/bin/bash
set -e

# Initialize database if it doesn't exist
if [ ! -f /data/app.db ]; then
    echo "Initializing database..."
    flask shell <<SHELL
from app import db
db.create_all()
exit()
SHELL
fi

# Start gunicorn
exec gunicorn --bind 0.0.0.0:5000 --workers 2 app:app
EOF

RUN chmod +x /app/start.sh

# Run the application
CMD ["/app/start.sh"]
