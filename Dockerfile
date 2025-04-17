# Use Python 3.12 base image
FROM python:3.12-slim-bookworm

WORKDIR /app

# Install Azure CLI dependencies and Azure CLI
RUN apt-get update && apt-get install -y \
    curl \
    apt-transport-https \
    lsb-release \
    gnupg \
    && curl -sL https://aka.ms/InstallAzureCLIDeb | bash \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy the project files
COPY . /app

# Install dependencies and the project
RUN pip install --no-cache-dir -e .

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Set the entrypoint
ENTRYPOINT ["polymarket-mcp-server"]

# Label the image
LABEL maintainer="pab1it0" \
      description="Polymarket MCP Server" \
      version="0.1.0"
