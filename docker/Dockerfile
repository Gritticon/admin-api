ARG PYTHON_VERSION=3.9.6
FROM python:${PYTHON_VERSION}-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN python -m pip install --no-cache-dir -r requirements.txt \
 && apt-get update \
 && apt-get install -y redis-server \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

# Copy application code
COPY . .

EXPOSE 80

# Run the application
CMD ["uvicorn", "main:app", "--host=0.0.0.0", "--port=80"]
