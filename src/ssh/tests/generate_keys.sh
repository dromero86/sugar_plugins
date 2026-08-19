#!/bin/bash

# Script to generate SSH keys for integration testing

echo "Generating SSH keys for integration testing..."

# Create keys directory if it doesn't exist
mkdir -p keys

# Generate private key
ssh-keygen -t rsa -b 4096 -f keys/test_key -N "" -C "test@integration.local"

# Generate public key from private key
ssh-keygen -y -f keys/test_key > keys/test_key.pub

# Set proper permissions
chmod 600 keys/test_key
chmod 644 keys/test_key.pub

echo "SSH keys generated successfully!"
echo "Private key: keys/test_key"
echo "Public key: keys/test_key.pub"

# Display the public key for easy copying
echo ""
echo "Public key content:"
cat keys/test_key.pub