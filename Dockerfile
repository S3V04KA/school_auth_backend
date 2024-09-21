FROM python:3.12.5-slim

# Log to stdout
ENV PYTHON_BUFFERED=1

# Install pip requirements
WORKDIR /backend

RUN apt update && \
    apt install -y postgresql-client build-essential python3-dev

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install nginx and copy configuration
RUN apt-get update && apt-get install -y --no-install-recommends nginx \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
COPY nginx-default.conf /etc/nginx/sites-available/default

# Copy app, generate static and set permissions
COPY . .

# Expose and run app
EXPOSE 6000
STOPSIGNAL SIGTERM