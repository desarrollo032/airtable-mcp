FROM python:3.11-slim

WORKDIR /app

# Install basic build deps (some packages may need build tools)
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

ENV PORT=8000
EXPOSE 8000

# Use python3 explicitly
CMD ["python3", "app.py"]
