FROM python:3.10.13-slim-bullseye

# Set environment variables to prevent interactive prompts
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV GIT_TERMINAL_PROMPT 0

# Install system dependencies required for building Python packages efficiently
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    gfortran \
    libopenblas-dev \
    liblapack-dev \
    libffi-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Configure git to use https instead of git protocol to avoid firewall issues
RUN git config --global url."https://github.com/".insteadOf git://github.com/

# Copy only the requirements file to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port the app runs on
EXPOSE 8050

# Command to run the application
CMD ["python", "app.py"]
