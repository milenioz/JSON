FROM python:3.8.10

# Set the working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy application files and requirements
COPY . .

# Create and activate a virtual environment
RUN python -m venv /app/venv && \
    /app/venv/bin/pip install --upgrade pip && \
    /app/venv/bin/pip install -r requirements_3810.txt
    
# Expose the default Dash port
EXPOSE 8051

# Add health check
HEALTHCHECK CMD curl --fail http://localhost:8051 || exit 1

# Command to run the Dash app
ENTRYPOINT ["python", "app.py"]
