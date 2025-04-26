FROM python:3.10-slim-buster

# Install system dependencies (optimized to reduce layers)
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-pip \
    git \
    gcc \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip3 install --upgrade pip

# Set up working directory
WORKDIR /music
RUN chmod 777 /music

# Install main requirements
COPY requirements.txt .
RUN pip3 install -r requirements.txt

# Install pirate requirements (if exists)
COPY mbot/pirate/requirements.txt ./pirate-requirements.txt
RUN if [ -f pirate-requirements.txt ]; then pip3 install -r pirate-requirements.txt; fi

# Copy the rest of the application
COPY . .

# Run the bot
CMD ["python3", "-m", "mbot"]
