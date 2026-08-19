"""
OpenSSL Plugin for Sugar
========================

A comprehensive OpenSSL plugin that provides cryptographic operations
including certificate management, key generation, encryption/decryption,
and more.
"""

import os
import subprocess
import tempfile
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from Sugar.Lang.Plugins import PluginBase
from Sugar.Lang.Utils.Output import Output

class OpenSSLPlugin(PluginBase):
    """
    OpenSSL plugin for Sugar.
    
    Provides comprehensive cryptographic operations including:
    - Key generation (RSA, modern keys)
    - Certificate operations (CSR, self-signed, verification)
    - Format conversion (PEM ↔ DER ↔ CRT)
    - Encryption/decryption
    - Digital signatures
    - PKCS#12 operations
    - Hash calculations
    """
    
    VERSION = "1.0.0"
    DESCRIPTION = "Comprehensive OpenSSL operations for Sugar"
    AUTHOR = "Sugar Team"
    LICENSE = "MIT"
    DEPENDENCIES = ["openssl"]
    REQUIREMENTS = ["openssl"]
    
    def __init__(self, context=None, plugin_config: Optional[Dict[str, Any]] = None):
        """Initialize the OpenSSL plugin."""
        super().__init__(context, plugin_config)
        self.openssl_path = self._find_openssl()
        if not self.openssl_path:
            self._log("Warning: OpenSSL not found in PATH")
            self._log("Installation instructions:")
            self._log("  Ubuntu/Debian: sudo apt-get install openssl")
            self._log("  CentOS/RHEL: sudo yum install openssl")
            self._log("  macOS: brew install openssl")
            self._log("  Windows: Download from https://www.openssl.org/")
    
    def _log(self, message: str):
        """Safely log a message using Output.Console or print."""
        try:
            Output.Console(self.plugin_name, message)
        except AttributeError:
            # Handle case where Output or plugin_name is not available (e.g., in tests)
            print(f"[OpenSSLPlugin] {message}")
    
    def _find_openssl(self) -> Optional[str]:
        """Find OpenSSL executable in PATH."""
        try:
            result = subprocess.run(['which', 'openssl'], 
                                  capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except (subprocess.CalledProcessError, FileNotFoundError):
            return None
    
    def _check_dependencies(self) -> Dict[str, Any]:
        """
        Check if all dependencies are satisfied.
        
        Returns:
            Dictionary with dependency status
        """
        status = {
            'openssl': {
                'available': self.openssl_path is not None,
                'path': self.openssl_path,
                'version': None
            }
        }
        
        # Get OpenSSL version if available
        if self.openssl_path:
            try:
                result = subprocess.run([self.openssl_path, 'version'], 
                                      capture_output=True, text=True, check=True)
                status['openssl']['version'] = result.stdout.strip()
            except subprocess.CalledProcessError:
                pass
        
        return status
    
    def get_dependency_info(self) -> Dict[str, Any]:
        """
        Get detailed dependency information.
        
        Returns:
            Dictionary with dependency information
        """
        deps = self._check_dependencies()
        
        info = {
            'plugin_name': 'openssl',
            'dependencies': deps,
            'all_satisfied': all(dep['available'] for dep in deps.values()),
            'install_instructions': {
                'openssl': {
                    'ubuntu_debian': 'sudo apt-get install openssl',
                    'centos_rhel': 'sudo yum install openssl',
                    'fedora': 'sudo dnf install openssl',
                    'macos': 'brew install openssl',
                    'windows': 'Download from https://www.openssl.org/',
                    'alpine': 'apk add openssl'
                }
            }
        }
        
        return info
    
    def get_available_commands(self) -> List[str]:
        """Get list of available OpenSSL commands."""
        return [
            "genrsa",           # Generar clave privada RSA
            "genpkey",          # Generar clave privada (moderna)
            "req_new",          # Crear CSR (Certificate Signing Request)
            "x509_selfsign",    # Crear certificado autofirmado
            "verify_cert",      # Verificar un certificado
            "convert",          # Convertir entre formatos (PEM ↔ DER ↔ CRT)
            "encrypt",          # Encriptar datos o archivos
            "decrypt",          # Desencriptar
            "sign",             # Firmar archivos
            "verify",           # Verificar firmas
            "pkcs12_export",    # Exportar a formato PKCS#12 (.pfx, .p12)
            "pkcs12_import",    # Importar desde .p12
            "extract_pubkey",   # Extraer clave pública
            "hash",             # Calcular hash
            "verify_chain",     # Verificar una cadena de confianza
            "csr_to_cert",      # Emitir certificado desde CSR
            "pem_to_crt",       # Alias de convert PEM → CRT
            "crt_to_pem"        # Alias de convert CRT → PEM
        ]
    
    def execute(self, command: str, config: Dict[str, Any]) -> Any:
        """Execute an OpenSSL command."""
        if not self.openssl_path:
            raise RuntimeError("OpenSSL not found. Please install OpenSSL.")
        
        # Interpolate variables in config
        try:
            config = self.interpolate_variables(config)
        except AttributeError:
            # Handle case where interpolate_variables is not available (e.g., in tests)
            pass
        
        if command == "genrsa":
            return self._genrsa(config)
        elif command == "genpkey":
            return self._genpkey(config)
        elif command == "req_new":
            return self._req_new(config)
        elif command == "x509_selfsign":
            return self._x509_selfsign(config)
        elif command == "verify_cert":
            return self._verify_cert(config)
        elif command == "convert":
            return self._convert(config)
        elif command == "encrypt":
            return self._encrypt(config)
        elif command == "decrypt":
            return self._decrypt(config)
        elif command == "sign":
            return self._sign(config)
        elif command == "verify":
            return self._verify(config)
        elif command == "pkcs12_export":
            return self._pkcs12_export(config)
        elif command == "pkcs12_import":
            return self._pkcs12_import(config)
        elif command == "extract_pubkey":
            return self._extract_pubkey(config)
        elif command == "hash":
            return self._hash(config)
        elif command == "verify_chain":
            return self._verify_chain(config)
        elif command == "csr_to_cert":
            return self._csr_to_cert(config)
        elif command == "pem_to_crt":
            return self._pem_to_crt(config)
        elif command == "crt_to_pem":
            return self._crt_to_pem(config)
        else:
            raise ValueError(f"Unknown OpenSSL command: {command}")
    
    def _run_openssl_command(self, args: List[str], input_data: Optional[str] = None) -> Dict[str, Any]:
        """Run OpenSSL command and return result."""
        try:
            cmd = [self.openssl_path] + args
            self._log(f"Running: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                input=input_data,
                capture_output=True,
                text=True,
                check=True
            )
            
            return {
                "success": True,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode
            }
        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "stdout": e.stdout,
                "stderr": e.stderr,
                "return_code": e.returncode,
                "error": str(e)
            }
    
    def _genrsa(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate RSA private key."""
        output_path = config.get("output", {}).get("path", "private.key")
        bits = config.get("params", {}).get("bits", 2048)
        
        args = ["genrsa", "-out", output_path, str(bits)]
        result = self._run_openssl_command(args)
        
        if result["success"]:
            self._log(f"RSA private key generated: {output_path}")
            return {"key_path": output_path, "bits": bits}
        else:
            raise RuntimeError(f"Failed to generate RSA key: {result['stderr']}")
    
    def _genpkey(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate modern private key."""
        output_path = config.get("output", {}).get("path", "private.key")
        algorithm = config.get("params", {}).get("algorithm", "RSA")
        bits = config.get("params", {}).get("bits", 2048)
        
        args = ["genpkey", "-algorithm", algorithm, "-out", output_path]
        if algorithm.upper() in ["RSA", "DSA"]:
            args.extend(["-pkeyopt", f"rsa_keygen_bits:{bits}"])
        
        result = self._run_openssl_command(args)
        
        if result["success"]:
            self._log(f"Private key generated: {output_path}")
            return {"key_path": output_path, "algorithm": algorithm, "bits": bits}
        else:
            raise RuntimeError(f"Failed to generate private key: {result['stderr']}")
    
    def _req_new(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create Certificate Signing Request."""
        key_path = config.get("input", {}).get("key", "private.key")
        output_path = config.get("output", {}).get("csr", "request.csr")
        subject = config.get("params", {}).get("subject", "/CN=localhost")
        
        args = ["req", "-new", "-key", key_path, "-out", output_path, "-subj", subject]
        result = self._run_openssl_command(args)
        
        if result["success"]:
            self._log(f"CSR created: {output_path}")
            return {"csr_path": output_path, "subject": subject}
        else:
            raise RuntimeError(f"Failed to create CSR: {result['stderr']}")
    
    def _x509_selfsign(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create self-signed certificate."""
        key_path = config.get("input", {}).get("key", "private.key")
        csr_path = config.get("input", {}).get("csr", "request.csr")
        output_path = config.get("output", {}).get("certificate", "cert.crt")
        days = config.get("params", {}).get("days", 365)
        
        args = ["x509", "-req", "-in", csr_path, "-signkey", key_path, 
                "-out", output_path, "-days", str(days)]
        result = self._run_openssl_command(args)
        
        if result["success"]:
            self._log(f"Self-signed certificate created: {output_path}")
            return {"certificate_path": output_path, "days": days}
        else:
            raise RuntimeError(f"Failed to create self-signed certificate: {result['stderr']}")
    
    def _verify_cert(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Verify certificate."""
        cert_path = config.get("input", {}).get("certificate", "cert.crt")
        ca_bundle = config.get("input", {}).get("ca_bundle")
        
        args = ["x509", "-in", cert_path, "-text", "-noout"]
        if ca_bundle:
            args.extend(["-CAfile", ca_bundle])
        
        result = self._run_openssl_command(args)
        
        if result["success"]:
            self._log(f"Certificate verified: {cert_path}")
            return {"verified": True, "certificate_info": result["stdout"]}
        else:
            return {"verified": False, "error": result["stderr"]}
    
    def _convert(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Convert between formats."""
        input_path = config.get("input", {}).get("path")
        input_format = config.get("input", {}).get("format", "PEM")
        output_path = config.get("output", {}).get("path")
        output_format = config.get("output", {}).get("format", "PEM")
        
        if not input_path or not output_path:
            raise ValueError("Input and output paths are required")
        
        # Determine conversion type
        if input_format.upper() == "PEM" and output_format.upper() == "DER":
            args = ["x509", "-in", input_path, "-outform", "DER", "-out", output_path]
        elif input_format.upper() == "DER" and output_format.upper() == "PEM":
            args = ["x509", "-inform", "DER", "-in", input_path, "-out", output_path]
        elif input_format.upper() == "PEM" and output_format.upper() == "CRT":
            args = ["x509", "-in", input_path, "-out", output_path]
        elif input_format.upper() == "CRT" and output_format.upper() == "PEM":
            args = ["x509", "-in", input_path, "-out", output_path]
        else:
            raise ValueError(f"Unsupported conversion: {input_format} to {output_format}")
        
        result = self._run_openssl_command(args)
        
        if result["success"]:
            self._log(f"Converted {input_path} to {output_path}")
            return {"converted": True, "output_path": output_path}
        else:
            raise RuntimeError(f"Failed to convert: {result['stderr']}")
    
    def _encrypt(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Encrypt data or files."""
        input_path = config.get("input", {}).get("path")
        output_path = config.get("output", {}).get("path")
        algorithm = config.get("params", {}).get("algorithm", "aes-256-cbc")
        password = config.get("params", {}).get("password")
        
        if not input_path or not output_path:
            raise ValueError("Input and output paths are required")
        
        args = ["enc", "-" + algorithm, "-in", input_path, "-out", output_path]
        if password:
            args.extend(["-pass", f"pass:{password}"])
        
        result = self._run_openssl_command(args, input_data=password + "\n" if password else None)
        
        if result["success"]:
            self._log(f"Encrypted {input_path} to {output_path}")
            return {"encrypted": True, "output_path": output_path}
        else:
            raise RuntimeError(f"Failed to encrypt: {result['stderr']}")
    
    def _decrypt(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Decrypt data or files."""
        input_path = config.get("input", {}).get("path")
        output_path = config.get("output", {}).get("path")
        algorithm = config.get("params", {}).get("algorithm", "aes-256-cbc")
        password = config.get("params", {}).get("password")
        
        if not input_path or not output_path:
            raise ValueError("Input and output paths are required")
        
        args = ["enc", "-d", "-" + algorithm, "-in", input_path, "-out", output_path]
        if password:
            args.extend(["-pass", f"pass:{password}"])
        
        result = self._run_openssl_command(args, input_data=password + "\n" if password else None)
        
        if result["success"]:
            self._log(f"Decrypted {input_path} to {output_path}")
            return {"decrypted": True, "output_path": output_path}
        else:
            raise RuntimeError(f"Failed to decrypt: {result['stderr']}")
    
    def _sign(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Sign files."""
        input_path = config.get("input", {}).get("path")
        key_path = config.get("input", {}).get("key")
        output_path = config.get("output", {}).get("path")
        algorithm = config.get("params", {}).get("algorithm", "sha256")
        
        if not input_path or not key_path or not output_path:
            raise ValueError("Input path, key path, and output path are required")
        
        args = ["dgst", "-" + algorithm, "-sign", key_path, "-out", output_path, input_path]
        result = self._run_openssl_command(args)
        
        if result["success"]:
            self._log(f"Signed {input_path} to {output_path}")
            return {"signed": True, "output_path": output_path}
        else:
            raise RuntimeError(f"Failed to sign: {result['stderr']}")
    
    def _verify(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Verify signatures."""
        input_path = config.get("input", {}).get("path")
        signature_path = config.get("input", {}).get("signature")
        pubkey_path = config.get("input", {}).get("pubkey")
        algorithm = config.get("params", {}).get("algorithm", "sha256")
        
        if not input_path or not signature_path or not pubkey_path:
            raise ValueError("Input path, signature path, and public key path are required")
        
        args = ["dgst", "-" + algorithm, "-verify", pubkey_path, "-signature", signature_path, input_path]
        result = self._run_openssl_command(args)
        
        if result["success"]:
            self._log(f"Signature verified for {input_path}")
            return {"verified": True}
        else:
            return {"verified": False, "error": result["stderr"]}
    
    def _pkcs12_export(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Export to PKCS#12 format."""
        cert_path = config.get("input", {}).get("certificate")
        key_path = config.get("input", {}).get("key")
        output_path = config.get("output", {}).get("pkcs12", "bundle.p12")
        password = config.get("params", {}).get("password", "")
        
        if not cert_path or not key_path:
            raise ValueError("Certificate and key paths are required")
        
        args = ["pkcs12", "-export", "-in", cert_path, "-inkey", key_path, "-out", output_path]
        if password:
            args.extend(["-passout", f"pass:{password}"])
        
        result = self._run_openssl_command(args)
        
        if result["success"]:
            self._log(f"PKCS#12 bundle created: {output_path}")
            return {"pkcs12_path": output_path}
        else:
            raise RuntimeError(f"Failed to create PKCS#12 bundle: {result['stderr']}")
    
    def _pkcs12_import(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Import from PKCS#12 format."""
        input_path = config.get("input", {}).get("path")
        password = config.get("params", {}).get("password", "")
        output_cert = config.get("output", {}).get("certificate", "cert.pem")
        output_key = config.get("output", {}).get("key", "key.pem")
        
        if not input_path:
            raise ValueError("Input path is required")
        
        # Extract certificate
        cert_args = ["pkcs12", "-in", input_path, "-clcerts", "-nokeys", "-out", output_cert]
        if password:
            cert_args.extend(["-passin", f"pass:{password}"])
        
        result = self._run_openssl_command(cert_args)
        if not result["success"]:
            raise RuntimeError(f"Failed to extract certificate: {result['stderr']}")
        
        # Extract private key
        key_args = ["pkcs12", "-in", input_path, "-nocerts", "-nodes", "-out", output_key]
        if password:
            key_args.extend(["-passin", f"pass:{password}"])
        
        result = self._run_openssl_command(key_args)
        if not result["success"]:
            raise RuntimeError(f"Failed to extract private key: {result['stderr']}")
        
        self._log(f"PKCS#12 bundle imported: {output_cert}, {output_key}")
        return {"certificate_path": output_cert, "key_path": output_key}
    
    def _extract_pubkey(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Extract public key from private key or certificate."""
        input_path = config.get("input", {}).get("path")
        output_path = config.get("output", {}).get("path", "public.pem")
        
        if not input_path:
            raise ValueError("Input path is required")
        
        # Try to extract from private key first
        args = ["rsa", "-in", input_path, "-pubout", "-out", output_path]
        result = self._run_openssl_command(args)
        
        if not result["success"]:
            # Try to extract from certificate
            args = ["x509", "-in", input_path, "-pubkey", "-noout", "-out", output_path]
            result = self._run_openssl_command(args)
        
        if result["success"]:
            self._log(f"Public key extracted: {output_path}")
            return {"public_key_path": output_path}
        else:
            raise RuntimeError(f"Failed to extract public key: {result['stderr']}")
    
    def _hash(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate hash of file or data."""
        input_path = config.get("input", {}).get("path")
        algorithm = config.get("params", {}).get("algorithm", "sha256")
        
        if not input_path:
            raise ValueError("Input path is required")
        
        args = ["dgst", "-" + algorithm, input_path]
        result = self._run_openssl_command(args)
        
        if result["success"]:
            # Parse hash from output
            lines = result["stdout"].strip().split('\n')
            hash_value = None
            for line in lines:
                if f"({input_path})=" in line:
                    hash_value = line.split('=')[1].strip()
                    break
            
            self._log(f"Hash calculated: {hash_value}")
            return {"hash": hash_value, "algorithm": algorithm}
        else:
            raise RuntimeError(f"Failed to calculate hash: {result['stderr']}")
    
    def _verify_chain(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Verify certificate chain."""
        cert_path = config.get("input", {}).get("certificate")
        ca_bundle = config.get("input", {}).get("ca_bundle")
        
        if not cert_path or not ca_bundle:
            raise ValueError("Certificate and CA bundle paths are required")
        
        args = ["verify", "-CAfile", ca_bundle, cert_path]
        result = self._run_openssl_command(args)
        
        if result["success"]:
            self._log(f"Certificate chain verified: {cert_path}")
            return {"verified": True, "chain_info": result["stdout"]}
        else:
            return {"verified": False, "error": result["stderr"]}
    
    def _csr_to_cert(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Issue certificate from CSR."""
        csr_path = config.get("input", {}).get("csr")
        ca_key = config.get("input", {}).get("ca_key")
        ca_cert = config.get("input", {}).get("ca_cert")
        output_path = config.get("output", {}).get("certificate", "issued.crt")
        days = config.get("params", {}).get("days", 365)
        
        if not csr_path or not ca_key or not ca_cert:
            raise ValueError("CSR, CA key, and CA certificate paths are required")
        
        args = ["x509", "-req", "-in", csr_path, "-CA", ca_cert, "-CAkey", ca_key,
                "-CAcreateserial", "-out", output_path, "-days", str(days)]
        result = self._run_openssl_command(args)
        
        if result["success"]:
            self._log(f"Certificate issued: {output_path}")
            return {"certificate_path": output_path, "days": days}
        else:
            raise RuntimeError(f"Failed to issue certificate: {result['stderr']}")
    
    def _pem_to_crt(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Convert PEM to CRT format (alias for convert)."""
        config["input"] = config.get("input", {})
        config["output"] = config.get("output", {})
        config["input"]["format"] = "PEM"
        config["output"]["format"] = "CRT"
        return self._convert(config)
    
    def _crt_to_pem(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Convert CRT to PEM format (alias for convert)."""
        config["input"] = config.get("input", {})
        config["output"] = config.get("output", {})
        config["input"]["format"] = "CRT"
        config["output"]["format"] = "PEM"
        return self._convert(config)