# DealFlow AI - Docker Container
FROM python:3.11-slim

WORKDIR /app

# Copy requirements
COPY backend/requirements_minimal.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements_minimal.txt

# Copy application code
COPY backend/simple_main.py .
COPY backend/models ./models
COPY backend/agents ./agents
COPY backend/services ./services
COPY backend/config.py .

# Expose port
EXPOSE 8000

# Set environment variables
ENV PORT=8000
ENV ENVIRONMENT=production

# Run the application
CMD ["uvicorn", "simple_main:app", "--host", "0.0.0.0", "--port", "8000"]
