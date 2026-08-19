FROM alpine:latest

# Install SSH server and utilities
RUN apk add --no-cache \
    openssh \
    openssh-server \
    openssh-keygen \
    bash \
    curl \
    wget \
    vim \
    nano \
    htop \
    tree \
    && rm -rf /var/cache/apk/*

# Create SSH directory and set permissions
RUN mkdir -p /var/run/sshd /root/.ssh

# Generate SSH host keys
RUN ssh-keygen -A

# Create test user
RUN adduser -D -s /bin/bash testuser && \
    echo "testuser:testpass" | chpasswd

# Create root password
RUN echo "root:rootpass" | chpasswd

# Configure SSH server
RUN sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config && \
    sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config && \
    sed -i 's/#PubkeyAuthentication yes/PubkeyAuthentication yes/' /etc/ssh/sshd_config && \
    sed -i 's/#AuthorizedKeysFile/AuthorizedKeysFile/' /etc/ssh/sshd_config

# Create test files and directories
RUN mkdir -p /home/testuser/test_files && \
    echo "Hello from SSH server!" > /home/testuser/test_files/test.txt && \
    echo "This is a test file for SSH integration testing" >> /home/testuser/test_files/test.txt && \
    chown -R testuser:testuser /home/testuser/test_files

# Create some system files for testing
RUN echo "Test system info" > /tmp/system_info.txt && \
    echo "CPU: 4 cores" >> /tmp/system_info.txt && \
    echo "Memory: 8GB" >> /tmp/system_info.txt

# Expose SSH port
EXPOSE 22

# Start SSH server
CMD ["/usr/sbin/sshd", "-D", "-e"]