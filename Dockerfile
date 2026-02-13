# Use official Python runtime as a parent image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# Install system dependencies
# gcc and others might be needed for some python packages
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn

# Copy project
COPY . .

# Expose port (Render/Heroku usually use dynamic ports, but we expose 5000 for local)
EXPOSE 5000

# Run gunicorn
# Workers: 2-4 for a small app. Timeout 120s for LLM processing.
CMD gunicorn --bind 0.0.0.0:$PORT app:app --workers 2 --timeout 120
