# Stage 1: Build React Frontend
FROM node:20-alpine AS frontend-builder

# Set working directory for frontend
WORKDIR /app/frontend

# Copy frontend package files and install dependencies
COPY frontend/package.json ./
COPY frontend/package-lock.json ./
# If you use yarn or pnpm, adjust accordingly (e.g., copy yarn.lock or pnpm-lock.yaml and use yarn install or pnpm install)
RUN npm install

# Copy the rest of the frontend source code
COPY frontend/ ./

# Build the frontend
RUN npm run build

# Stage 2: Python Backend
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy built frontend from builder stage
COPY --from=frontend-builder /app/frontend/dist /app/frontend/dist

# Copy backend code
COPY backend/ /app/backend/

# Set working directory
WORKDIR /app/backend

# Install Python dependencies
RUN pip install --no-cache-dir -e .

# Expose port
EXPOSE 8000

# Start the Strands Agent API server
CMD ["python", "-m", "agent.main"]


