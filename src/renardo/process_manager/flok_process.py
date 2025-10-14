"""
Flok server process management (for future use).
"""

import shutil
import socket
from typing import Dict, Any
from .base import ManagedProcess, ProcessStatus


class FlokServerProcess(ManagedProcess):
    """Manages a Flok Node.js server process (for future use)."""
    
    def __init__(self, process_id: str, config: Dict[str, Any] = None):
        """
        Initialize a Flok server process.
        
        Config options:
            - port: Port to run the server on (default: 3000)
            - secure: Whether to use HTTPS (default: False)
            - host: Host to bind to (default: localhost)
            - flok_package: Flok package to use (default: 'flok-web@latest')
        """
        super().__init__(process_id, 'flok_server', config)
        
        # Default configuration
        self.config.setdefault('port', 3000)
        self.config.setdefault('secure', False)
        self.config.setdefault('host', 'localhost')
        self.config.setdefault('flok_package', 'flok-web@latest')
        self.config.setdefault('capture_output', True)
    
    def _build_command(self) -> list:
        """Build the Flok server command line."""
        # Check if npx is available
        if not shutil.which('npx'):
            raise RuntimeError("npx not found - Node.js is required for Flok server")
        
        command = ['npx', self.config['flok_package']]
        
        # Add port
        command.extend(['--port', str(self.config['port'])])
        
        # Add host
        if self.config['host'] != 'localhost':
            command.extend(['--host', self.config['host']])
        
        # Add secure flag
        if self.config['secure']:
            command.append('--secure')
        
        # Add additional arguments from config
        if 'args' in self.config:
            command.extend(self.config['args'])
        
        return command
    
    def _check_port_available(self) -> bool:
        """Check if the configured port is available."""
        port = self.config['port']
        host = self.config['host']
        
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(1)
                result = sock.connect_ex((host, port))
                return result != 0  # Port is available if connection fails
        except Exception as e:
            self.logger.warning(f"Could not check port availability: {e}")
            return True  # Assume available
    
    def start(self) -> bool:
        """Start the Flok server process."""
        # Check if port is available
        if not self._check_port_available():
            port = self.config['port']
            host = self.config['host']
            self.logger.error(f"Port {port} on {host} is already in use")
            self._set_status(ProcessStatus.ERROR, f"Port {port} already in use")
            return False
        
        success = super().start()
        
        if success:
            port = self.config['port']
            secure = self.config['secure']
            protocol = 'https' if secure else 'http'
            host = self.config['host']
            
            self.logger.info(f"Flok server should be available at {protocol}://{host}:{port}")
        
        return success
    
    def get_server_url(self) -> str:
        """Get the server URL."""
        protocol = 'https' if self.config['secure'] else 'http'
        host = self.config['host']
        port = self.config['port']
        return f"{protocol}://{host}:{port}"
    
    def is_nodejs_available(self) -> bool:
        """Check if Node.js is available."""
        return shutil.which('node') is not None and shutil.which('npx') is not None