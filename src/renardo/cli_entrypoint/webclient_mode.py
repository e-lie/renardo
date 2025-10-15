"""
Webclient mode for Renardo CLI - launches the modern web application.
"""

import os
import sys
import time
import signal
import subprocess
import threading
from pathlib import Path
from typing import Dict, Any

from ..logger import get_main_logger


def run_webclient_mode(config: Dict[str, Any]) -> int:
    """
    Run the webclient mode - starts both frontend and backend servers.

    Args:
        config: CLI configuration dictionary

    Returns:
        Exit code (0 for success, non-zero for error)
    """
    logger = get_main_logger()

    # Find project root directory - look for pyproject.toml to identify the root
    current_path = Path(__file__).resolve()
    project_root = None

    for parent in current_path.parents:
        if (parent / "pyproject.toml").exists():
            project_root = parent
            break

    if not project_root:
        logger.error("Could not find project root (pyproject.toml not found)")
        return 1

    webclient_dir = project_root / "webclient_fresh"
    flok_dir = project_root / "flok_renardo"

    if not webclient_dir.exists():
        logger.error(f"Webclient directory not found: {webclient_dir}")
        logger.error(f"Project root detected as: {project_root}")
        return 1

    if not flok_dir.exists():
        logger.error(f"Flok directory not found: {flok_dir}")
        return 1

    logger.info(f"Starting webclient from: {webclient_dir}")
    logger.info(f"Starting flok from: {flok_dir}")

    processes = []

    try:
        # Start the backend GraphQL server
        logger.info("Starting FastAPI + Strawberry GraphQL backend...")
        backend_process = start_backend_server(config)
        if backend_process:
            processes.append(backend_process)
            logger.info("Backend server started successfully")
        else:
            logger.error("Failed to start backend server")
            return 1

        # Wait a moment for backend to start
        time.sleep(2)

        # Start the flok server
        logger.info("Starting Flok collaborative editor...")
        flok_process = start_flok_server(flok_dir, config)
        if flok_process:
            processes.append(flok_process)
            logger.info("Flok server started successfully")
        else:
            logger.error("Failed to start flok server")
            cleanup_processes(processes)
            return 1

        # Wait a moment for flok to start
        time.sleep(3)

        # Start the frontend development server
        logger.info("Starting Vite development server...")
        frontend_process = start_frontend_server(webclient_dir, config)
        if frontend_process:
            processes.append(frontend_process)
            logger.info("Frontend server started successfully")
        else:
            logger.error("Failed to start frontend server")
            cleanup_processes(processes)
            return 1

        logger.info("Webclient application is running!")
        logger.info("Frontend: http://localhost:3001")
        logger.info("Backend GraphQL: http://localhost:8000/graphql")
        logger.info("Flok Editor: http://localhost:3002")
        logger.info("Press Ctrl+C to stop all servers")

        # Wait for processes to complete or user interruption
        try:
            while all(p.poll() is None for p in processes):
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Shutting down servers...")

        return 0

    except Exception as e:
        logger.error(f"Error in webclient mode: {e}")
        return 1
    finally:
        cleanup_processes(processes)


def start_backend_server(config: Dict[str, Any]) -> subprocess.Popen:
    """Start the FastAPI backend server."""
    logger = get_main_logger()

    try:
        # Use uvicorn to run the FastAPI app
        cmd = [
            "uv", "run", "uvicorn",
            "renardo.webserver_fresh.app:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload"
        ]

        if config.get('debug'):
            cmd.extend(["--log-level", "debug"])
        else:
            cmd.extend(["--log-level", "info"])

        logger.debug(f"Backend command: {' '.join(cmd)}")

        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            bufsize=1
        )

        # Start a thread to handle backend output
        threading.Thread(
            target=log_process_output,
            args=(process, "BACKEND"),
            daemon=True
        ).start()

        return process

    except Exception as e:
        logger.error(f"Failed to start backend server: {e}")
        return None


def start_flok_server(flok_dir: Path, config: Dict[str, Any]) -> subprocess.Popen:
    """Start the Flok collaborative editor server."""
    logger = get_main_logger()

    try:
        # Check if flok dependencies are installed
        flok_web_dir = flok_dir / "packages" / "web"
        if not flok_web_dir.exists():
            logger.error(f"Flok web package not found: {flok_web_dir}")
            return None

        # First, install dependencies if node_modules doesn't exist
        if not (flok_dir / "node_modules").exists():
            logger.info("Installing flok dependencies...")
            install_cmd = ["npm", "install"]
            install_process = subprocess.run(
                install_cmd,
                cwd=flok_dir,
                capture_output=True,
                text=True
            )

            if install_process.returncode != 0:
                logger.error(f"Failed to install flok dependencies: {install_process.stderr}")
                return None

            logger.info("Flok dependencies installed successfully")

        # Build flok if needed
        if not (flok_web_dir / "dist").exists():
            logger.info("Building flok...")
            build_cmd = ["npm", "run", "build"]
            build_process = subprocess.run(
                build_cmd,
                cwd=flok_dir,
                capture_output=True,
                text=True
            )

            if build_process.returncode != 0:
                logger.warning(f"Flok build had issues: {build_process.stderr}")
                # Continue anyway as dev mode might work

        # Start the flok web server
        cmd = ["npm", "run", "dev", "--", "--port", "3002", "--host", "0.0.0.0"]

        logger.debug(f"Flok command: {' '.join(cmd)}")

        process = subprocess.Popen(
            cmd,
            cwd=flok_web_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            bufsize=1
        )

        # Start a thread to handle flok output
        threading.Thread(
            target=log_process_output,
            args=(process, "FLOK"),
            daemon=True
        ).start()

        return process

    except Exception as e:
        logger.error(f"Failed to start flok server: {e}")
        return None


def start_frontend_server(webclient_dir: Path, config: Dict[str, Any]) -> subprocess.Popen:
    """Start the Vite frontend development server."""
    logger = get_main_logger()

    try:
        # First, install dependencies if node_modules doesn't exist
        if not (webclient_dir / "node_modules").exists():
            logger.info("Installing frontend dependencies...")
            install_cmd = ["npm", "install"]
            install_process = subprocess.run(
                install_cmd,
                cwd=webclient_dir,
                capture_output=True,
                text=True
            )

            if install_process.returncode != 0:
                logger.error(f"Failed to install dependencies: {install_process.stderr}")
                return None

            logger.info("Dependencies installed successfully")

        # Start the development server
        cmd = ["npm", "run", "dev"]

        logger.debug(f"Frontend command: {' '.join(cmd)}")

        process = subprocess.Popen(
            cmd,
            cwd=webclient_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            bufsize=1
        )

        # Start a thread to handle frontend output
        threading.Thread(
            target=log_process_output,
            args=(process, "FRONTEND"),
            daemon=True
        ).start()

        return process

    except Exception as e:
        logger.error(f"Failed to start frontend server: {e}")
        return None


def log_process_output(process: subprocess.Popen, prefix: str):
    """Log output from a subprocess."""
    logger = get_main_logger()

    # Log stdout
    def log_stdout():
        for line in iter(process.stdout.readline, ''):
            if line.strip():
                logger.info(f"[{prefix}] {line.strip()}")

                # Also send to GraphQL if possible
                try:
                    from ..webserver_fresh.log_handler import capture_subprocess_output
                    capture_subprocess_output(prefix, line.strip(), "INFO")
                except:
                    pass  # Silently fail if GraphQL not available

    # Log stderr
    def log_stderr():
        for line in iter(process.stderr.readline, ''):
            if line.strip():
                logger.warning(f"[{prefix}] {line.strip()}")

                # Also send to GraphQL if possible
                try:
                    from ..webserver_fresh.log_handler import capture_subprocess_output
                    capture_subprocess_output(prefix, line.strip(), "WARNING")
                except:
                    pass  # Silently fail if GraphQL not available

    # Start threads for both stdout and stderr
    stdout_thread = threading.Thread(target=log_stdout, daemon=True)
    stderr_thread = threading.Thread(target=log_stderr, daemon=True)

    stdout_thread.start()
    stderr_thread.start()


def cleanup_processes(processes):
    """Clean up running processes."""
    logger = get_main_logger()

    for process in processes:
        if process and process.poll() is None:
            logger.debug(f"Terminating process {process.pid}")
            try:
                process.terminate()
                # Wait briefly for graceful shutdown
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    logger.debug(f"Force killing process {process.pid}")
                    process.kill()
            except Exception as e:
                logger.debug(f"Error cleaning up process {process.pid}: {e}")