#!/bin/bash

# Script to build and run Docker SSH server for integration testing

set -e

echo "=== SSH Integration Test with Docker ==="
echo ""

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed or not in PATH"
    exit 1
fi

# Build the Docker image
echo "Building Docker SSH server image..."
docker build -t ssh-test-server .

# Stop and remove existing container if it exists
echo "Cleaning up existing containers..."
docker stop ssh-test-server 2>/dev/null || true
docker rm ssh-test-server 2>/dev/null || true

# Generate SSH keys if they don't exist
if [ ! -f "keys/test_key" ]; then
    echo "Generating SSH keys..."
    chmod +x generate_keys.sh
    ./generate_keys.sh
fi

# Run the SSH server container
echo "Starting SSH server container..."
docker run -d \
    --name ssh-test-server \
    -p 2222:22 \
    -v "$(pwd)/keys/test_key.pub:/root/.ssh/authorized_keys:ro" \
    -v "$(pwd)/keys/test_key.pub:/home/testuser/.ssh/authorized_keys:ro" \
    ssh-test-server

# Wait for SSH server to start
echo "Waiting for SSH server to start..."
sleep 5

# Test SSH connection
echo "Testing SSH connection..."
if ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -p 2222 root@localhost "echo 'SSH connection successful!'"; then
    echo "✅ SSH connection test passed!"
else
    echo "❌ SSH connection test failed!"
    echo "Container logs:"
    docker logs ssh-test-server
    exit 1
fi

echo ""
echo "=== Docker SSH Server Ready ==="
echo "SSH Server running on localhost:2222"
echo "Users:"
echo "  - root (password: rootpass)"
echo "  - testuser (password: testpass)"
echo "Private key: keys/test_key"
echo ""
echo "Test commands:"
echo "  ssh -i keys/test_key -p 2222 root@localhost"
echo "  ssh -i keys/test_key -p 2222 testuser@localhost"
echo ""

# Keep container running for manual testing
echo "Container is running. Press Ctrl+C to stop and clean up."
echo "To stop manually: docker stop ssh-test-server && docker rm ssh-test-server"