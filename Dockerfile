FROM ubuntu:22.04

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3 python3-pip python3-dev python3-venv \
    libpython3-dev libpython3.10 \
    libxkbcommon0 libxkbcommon-x11-0 \
    libdbus-1-3 libfontconfig1 \
    fuse libfuse2 \
    wget \
    file \
    && rm -rf /var/lib/apt/lists/*

# Set workdir
WORKDIR /app

# Copy source
COPY . .

# Get pip and install pyinstaller only (PyInstaller will bundle the rest)
RUN pip3 install --upgrade pip && \
    pip3 install pyinstaller PyQt6 --only-binary=:all:

# Build with PyInstaller - add verbose output
RUN pyinstaller FreshNamer.spec -v

# Copy built executable back to mount point
RUN cp -r dist/FreshNamer /app/dist-linux/ 2>/dev/null || cp -r dist/FreshNamer /app/
