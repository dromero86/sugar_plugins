#!/usr/bin/env python3
"""
SSH Plugin Integration Test with Docker
=======================================

This script tests the SSH plugin against a real SSH server running in Docker.
It demonstrates various SSH operations including connection, command execution,
file transfer, and system monitoring.
"""

import os
import sys
import time
import json
import tempfile
from pathlib import Path

# Add the parent directory to the path to import the SSH plugin
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    from plugins.ssh.SSHPlugin import SSHPlugin
    from Sugar.Lang.Utils.Output import Output
except ImportError as e:
    print(f"Error importing SSH plugin: {e}")
    print("Make sure you're running this from the correct directory")
    sys.exit(1)

class SSHIntegrationTest:
    def __init__(self):
        self.plugin = SSHPlugin()
        self.test_results = []
        self.private_key_path = os.path.join(os.path.dirname(__file__), 'keys', 'test_key')
        
    def log_test(self, test_name, success, message=""):
        """Log test results"""
        status = "PASS" if success else "FAIL"
        print(f"{status} {test_name}: {message}")
        self.test_results.append({
            'test': test_name,
            'success': success,
            'message': message
        })
        
    def test_connection_with_password(self):
        """Test SSH connection using password authentication"""
        print("\n=== Testing Password Authentication ===")
        
        config = {
            "session": "docker_test_password",
            "host": "localhost",
            "port": 2222,
            "username": "root",
            "password": "rootpass",
            "timeout": 10
        }
        
        try:
            result = self.plugin.execute("connect", config)
            if result and result.get('success'):
                self.log_test("Password Authentication", True, "Connected successfully")
                return True
            else:
                self.log_test("Password Authentication", False, f"Connection failed: {result}")
                return False
        except Exception as e:
            self.log_test("Password Authentication", False, f"Exception: {str(e)}")
            return False
            
    def test_connection_with_key(self):
        """Test SSH connection using key authentication"""
        print("\n=== Testing Key Authentication ===")
        
        if not os.path.exists(self.private_key_path):
            self.log_test("Key Authentication", False, "Private key file not found")
            return False
            
        config = {
            "session": "docker_test_key",
            "host": "localhost",
            "port": 2222,
            "username": "root",
            "private_key": self.private_key_path,
            "timeout": 10
        }
        
        try:
            result = self.plugin.execute("connect", config)
            if result and result.get('success'):
                self.log_test("Key Authentication", True, "Connected successfully")
                return True
            else:
                self.log_test("Key Authentication", False, f"Connection failed: {result}")
                return False
        except Exception as e:
            self.log_test("Key Authentication", False, f"Exception: {str(e)}")
            return False
            
    def test_command_execution(self):
        """Test command execution on the remote server"""
        print("\n=== Testing Command Execution ===")
        
        commands = [
            ("whoami", "root"),
            ("pwd", "/root"),
            ("uname -a", "Linux"),
            ("echo 'Hello from SSH plugin!'", "Hello from SSH plugin!"),
            ("ls -la /home/testuser/test_files/", "test.txt")
        ]
        
        for command, expected in commands:
            config = {
                "session": "docker_test_key",
                "command": command
            }
            
            try:
                result = self.plugin.execute("execute", config)
                if result and result.get('success'):
                    output = result.get('output', '')
                    if expected in output:
                        self.log_test(f"Command: {command}", True, f"Output contains '{expected}'")
                    else:
                        self.log_test(f"Command: {command}", False, f"Expected '{expected}' not found in output")
                else:
                    self.log_test(f"Command: {command}", False, f"Execution failed: {result}")
            except Exception as e:
                self.log_test(f"Command: {command}", False, f"Exception: {str(e)}")
                
    def test_file_operations(self):
        """Test file operations on the remote server"""
        print("\n=== Testing File Operations ===")
        
        # Test listing files
        config = {
            "session": "docker_test_key",
            "path": "/home/testuser/test_files"
        }
        
        try:
            result = self.plugin.execute("ls", config)
            if result and result.get('success'):
                self.log_test("List Files", True, f"Found {len(result.get('files', []))} files")
            else:
                self.log_test("List Files", False, f"Failed: {result}")
        except Exception as e:
            self.log_test("List Files", False, f"Exception: {str(e)}")
            
        # Test creating directory
        config = {
            "session": "docker_test_key",
            "path": "/tmp/ssh_test_dir"
        }
        
        try:
            result = self.plugin.execute("mkdir", config)
            if result and result.get('success'):
                self.log_test("Create Directory", True, "Directory created successfully")
            else:
                self.log_test("Create Directory", False, f"Failed: {result}")
        except Exception as e:
            self.log_test("Create Directory", False, f"Exception: {str(e)}")
            
    def test_file_transfer(self):
        """Test file upload and download"""
        print("\n=== Testing File Transfer ===")
        
        # Create a test file locally
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("This is a test file for SSH plugin integration testing\n")
            f.write(f"Created at: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            local_file = f.name
            
        try:
            # Upload file
            config = {
                "session": "docker_test_key",
                "local_path": local_file,
                "remote_path": "/tmp/uploaded_test.txt"
            }
            
            result = self.plugin.execute("upload", config)
            if result and result.get('success'):
                self.log_test("File Upload", True, "File uploaded successfully")
            else:
                self.log_test("File Upload", False, f"Failed: {result}")
                
            # Download file
            download_path = f"/tmp/downloaded_{os.path.basename(local_file)}"
            config = {
                "session": "docker_test_key",
                "remote_path": "/tmp/uploaded_test.txt",
                "local_path": download_path
            }
            
            result = self.plugin.execute("download", config)
            if result and result.get('success'):
                self.log_test("File Download", True, "File downloaded successfully")
            else:
                self.log_test("File Download", False, f"Failed: {result}")
                
        except Exception as e:
            self.log_test("File Transfer", False, f"Exception: {str(e)}")
        finally:
            # Clean up local test file
            if os.path.exists(local_file):
                os.unlink(local_file)
                
    def test_system_info(self):
        """Test system information retrieval"""
        print("\n=== Testing System Information ===")
        
        config = {
            "session": "docker_test_key"
        }
        
        try:
            result = self.plugin.execute("system_info", config)
            if result and result.get('success'):
                info = result.get('info', {})
                self.log_test("System Info", True, f"Retrieved {len(info)} system metrics")
            else:
                self.log_test("System Info", False, f"Failed: {result}")
        except Exception as e:
            self.log_test("System Info", False, f"Exception: {str(e)}")
            
    def test_process_management(self):
        """Test process listing and management"""
        print("\n=== Testing Process Management ===")
        
        # List processes
        config = {
            "session": "docker_test_key"
        }
        
        try:
            result = self.plugin.execute("list_processes", config)
            if result and result.get('success'):
                processes = result.get('processes', [])
                self.log_test("List Processes", True, f"Found {len(processes)} processes")
            else:
                self.log_test("List Processes", False, f"Failed: {result}")
        except Exception as e:
            self.log_test("List Processes", False, f"Exception: {str(e)}")
            
    def cleanup(self):
        """Clean up SSH connections"""
        print("\n=== Cleaning Up ===")
        
        sessions = ["docker_test_password", "docker_test_key"]
        for session in sessions:
            try:
                config = {"session": session}
                self.plugin.execute("disconnect", config)
                self.log_test(f"Disconnect {session}", True, "Disconnected successfully")
            except Exception as e:
                self.log_test(f"Disconnect {session}", False, f"Exception: {str(e)}")
                
    def run_all_tests(self):
        """Run all integration tests"""
        print("Starting SSH Plugin Integration Tests")
        print("=" * 50)
        
        # Test connections
        self.test_connection_with_password()
        self.test_connection_with_key()
        
        # Test operations (only if key connection works)
        if any(r['test'] == 'Key Authentication' and r['success'] for r in self.test_results):
            self.test_command_execution()
            self.test_file_operations()
            self.test_file_transfer()
            self.test_system_info()
            self.test_process_management()
        
        # Cleanup
        self.cleanup()
        
        # Print summary
        print("\n" + "=" * 50)
        print("INTEGRATION TEST SUMMARY")
        print("=" * 50)
        
        passed = sum(1 for r in self.test_results if r['success'])
        total = len(self.test_results)
        
        for result in self.test_results:
            status = "" if result['success'] else ""
            print(f"{status} {result['test']}: {result['message']}")
            
        print(f"\nOverall: {passed}/{total} tests passed")
        
        if passed == total:
            print("All integration tests passed!")
            return True
        else:
            print(" Some tests failed. Check the output above.")
            return False

def main():
    """Main function to run integration tests"""
    print("SSH Plugin Integration Test with Docker")
    print("Make sure the Docker SSH server is running on localhost:2222")
    print("Run: ./run_docker_test.sh to start the server")
    print()
    
    # Check if Docker server is accessible
    import socket
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex(('localhost', 2222))
        sock.close()
        
        if result != 0:
            print("SSH server not accessible on localhost:2222")
            print("Please run: ./run_docker_test.sh to start the Docker SSH server")
            return False
    except Exception as e:
        print(f"Error checking SSH server: {e}")
        return False
        
    print("SSH server is accessible")
    
    # Run tests
    tester = SSHIntegrationTest()
    success = tester.run_all_tests()
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)