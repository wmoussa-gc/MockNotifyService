# Use official Python image
FROM python:3.11-slim
COPY --from=public.ecr.aws/awsguru/aws-lambda-adapter:0.9.1@sha256:46d6625e68cbbdd2efab4a20245977664513f13ffef47915b000d431adcea0b4 /lambda-adapter /opt/extensions/lambda-adapter

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY . /app/

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir flask gunicorn werkzeug flask-sqlalchemy psycopg2-binary email-validator

# Expose port
EXPOSE 8080

# Set environment variable for Flask
ENV SESSION_SECRET=change-this-secret

# Start the app with Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "main:app"]