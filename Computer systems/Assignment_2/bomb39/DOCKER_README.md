# Bomb Lab Docker Container

This directory contains a Docker setup to run the bomb executable that requires glibc 2.38.

## Files

- `Dockerfile` - Docker container definition with Ubuntu 24.04 and glibc 2.39
- `docker-compose.yml` - Docker Compose configuration for easy container management
- `run-bomb.sh` - Simple script to build and run the container
- `bomb` - The bomb executable
- `bomb.c` - Source code with main routine
- `README` - Original bomb lab instructions

## Quick Start

### Option 1: Using the run script (recommended)
```bash
./run-bomb.sh
```

### Option 2: Using Docker directly
```bash
# Build the container
docker build -t bomb39 .

# Run the container interactively
docker run -it --rm -v "$(pwd):/bomb" -w /bomb bomb39 /bin/bash
```

### Option 3: Using Docker Compose
```bash
# Start the container in the background
docker-compose up -d

# Enter the container
docker exec -it bomb39-container /bin/bash

# Stop the container when done
docker-compose down
```

## Inside the Container

Once inside the container, you can:

1. **Run the bomb:**
   ```bash
   ./bomb
   ```

2. **Debug with GDB:**
   ```bash
   gdb bomb
   ```

3. **Create solution files:**
   ```bash
   # Create a text file with your solutions
   echo "your_phase1_solution" > solution.txt
   echo "your_phase2_solution" >> solution.txt
   # ... and so on
   
   # Test with the solution file
   ./bomb solution.txt
   ```

4. **Use other debugging tools:**
   ```bash
   # Check file info
   file bomb
   
   # Check dependencies
   ldd bomb
   
   # Disassemble
   objdump -d bomb
   
   # Trace system calls
   strace ./bomb
   
   # Trace library calls
   ltrace ./bomb
   ```

## Notes

- The container runs as a non-root user `bombuser` for security
- Your files are mounted from the host, so any solution files you create will persist
- The container includes gdb and other debugging tools
- Press Ctrl+C to stop the bomb if it's waiting for input
- Press Ctrl+D or type `exit` to leave the container

## Troubleshooting

If you encounter permission issues:
```bash
# Make sure the bomb is executable
chmod +x bomb

# If running on SELinux systems, you might need:
sudo setsebool -P container_manage_cgroup on
```
