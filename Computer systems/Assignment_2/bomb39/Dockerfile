# Use Ubuntu 24.04 which has glibc 2.39
FROM ubuntu:24.04

# Install necessary packages for running the bomb and debugging
RUN apt-get update && apt-get install -y \
    gdb \
    file \
    strace \
    ltrace \
    binutils \
    && rm -rf /var/lib/apt/lists/*

# Create a working directory
WORKDIR /bomb

# Copy the bomb files into the container
COPY bomb ./
COPY bomb.c ./
COPY README ./

# Make sure the bomb is executable
RUN chmod +x bomb

# Create a non-root user for security
RUN useradd -m -s /bin/bash bombuser && \
    chown -R bombuser:bombuser /bomb

# Switch to non-root user
USER bombuser

# Set the default command
CMD ["/bin/bash"]
