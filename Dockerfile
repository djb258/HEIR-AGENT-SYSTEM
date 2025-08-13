# HEIR Platform Docker Container
FROM node:18-alpine AS base

# Install system dependencies
RUN apk add --no-cache \
    postgresql-client \
    curl \
    bash

# Create app directory
WORKDIR /app

# Copy package files (if they exist)
COPY package*.json ./
RUN npm install --only=production || echo "No package.json found, skipping npm install"

# Copy platform files
COPY heir-drop-in.js ./
COPY scripts/ ./scripts/
COPY database/ ./database/
COPY agents/ ./agents/
COPY *.md ./
COPY *.json ./

# Make scripts executable
RUN chmod +x scripts/*.sh

# Create non-root user for security
RUN addgroup -g 1001 -S heir && \
    adduser -S heir -u 1001 -G heir

# Set ownership
RUN chown -R heir:heir /app

# Switch to non-root user
USER heir

# Health check endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:3000/health || exit 1

# Expose port (if running web service)
EXPOSE 3000

# Default command: Initialize platform and start monitoring
CMD ["sh", "-c", "echo 'Initializing HEIR Platform...' && node heir-drop-in.js && echo 'HEIR Platform initialized successfully'"]