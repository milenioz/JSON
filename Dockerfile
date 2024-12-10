FROM python:3.12

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

# RUN git clone https://github.com/streamlit/streamlit-example.git .
COPY . .
RUN pip install -r requirements.txt


# Expose the default Dash port
EXPOSE 8051

# Add health check
HEALTHCHECK CMD curl --fail http://localhost:8051 || exit 1

# Command to run the Dash app
ENTRYPOINT ["python", "app.py"]
