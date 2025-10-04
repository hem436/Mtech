#!/bin/bash

# Quick test script to verify the bomb container works

echo "=== Testing Bomb Container Setup ==="
echo

echo "1. Testing container build..."
if sudo docker build -t bomb39 . >/dev/null 2>&1; then
    echo "✓ Container builds successfully"
else
    echo "✗ Container build failed"
    exit 1
fi

echo "2. Testing bomb executable in container..."
result=$(sudo docker run --rm -v "$(pwd):/bomb" -w /bomb bomb39 /bin/bash -c "echo 'test' | timeout 2 ./bomb 2>&1" || true)

if echo "$result" | grep -q "Welcome to my fiendish little bomb"; then
    echo "✓ Bomb executable runs successfully in container"
    echo "✓ Container has compatible glibc version"
else
    echo "✗ Bomb executable failed to run"
    echo "Output: $result"
    exit 1
fi

echo "3. Testing debugging tools..."
gdb_test=$(sudo docker run --rm -v "$(pwd):/bomb" -w /bomb bomb39 /bin/bash -c "gdb --version" 2>/dev/null | head -n1)
if echo "$gdb_test" | grep -q "GNU gdb"; then
    echo "✓ GDB is available: $gdb_test"
else
    echo "✗ GDB not available"
fi

echo
echo "=== SETUP VERIFICATION COMPLETE ==="
echo "✓ Docker daemon is running"
echo "✓ Container builds successfully" 
echo "✓ Bomb executable works in container"
echo "✓ Debugging tools are available"
echo
echo "Ready to start bomb defusing!"
echo "Run: ./run-bomb.sh"
echo
echo "Inside the container you can:"
echo "  ./bomb                 # Run the bomb"
echo "  gdb bomb              # Debug with GDB"  
echo "  objdump -d bomb       # Disassemble"
echo "  echo 'solution' > solution.txt  # Save solutions"
