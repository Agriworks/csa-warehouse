"""
Streamlit integration with FastAPI.
This module provides functionality to serve Streamlit apps within FastAPI.
"""
import atexit
import logging
import subprocess
import threading
import time
from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from typing import Dict, List

logger = logging.getLogger(__name__)

# Global dictionary to track Streamlit processes
_streamlit_processes = {}

# Global registry of mounted dashboards
_mounted_dashboards: Dict[str, dict] = {}


def cleanup_streamlit_processes():
    """Clean up all Streamlit processes on exit"""
    for process in _streamlit_processes.values():
        if process and process.poll() is None:
            try:
                process.terminate()
                process.wait(timeout=5)
                logger.info("Terminated Streamlit process")
            except subprocess.TimeoutExpired:
                process.kill()
                logger.info("Killed Streamlit process")
            except Exception as e:
                logger.error(f"Error cleaning up Streamlit process: {e}")


# Register cleanup on exit
atexit.register(cleanup_streamlit_processes)


def start_streamlit_server(dashboard_path: str, port: int = 8501) -> subprocess.Popen:
    """
    Start a Streamlit server as a subprocess.

    Args:
        dashboard_path: Path to the Streamlit dashboard script
        port: Port to run Streamlit on

    Returns:
        subprocess.Popen: The Streamlit subprocess
    """
    script_path = Path(dashboard_path).resolve()

    if not script_path.exists():
        raise FileNotFoundError(f"Dashboard file not found: {dashboard_path}")

    # Check if Streamlit is already running on this port
    port_key = f"port_{port}"
    if port_key in _streamlit_processes:
        process = _streamlit_processes[port_key]
        if process.poll() is None:
            logger.info(f"Streamlit already running on port {port}")
            return process

    # Start Streamlit server
    cmd = [
        "streamlit",
        "run",
        str(script_path),
        "--server.port", str(port),
        "--server.headless", "true",
        "--server.enableCORS", "false",
        "--server.enableXsrfProtection", "false",
        "--browser.gatherUsageStats", "false",
        "--server.address", "0.0.0.0",
    ]

    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        _streamlit_processes[port_key] = process

        # Give Streamlit a moment to start
        time.sleep(1)

        # Check if process is still running
        if process.poll() is None:
            logger.info(
                f"Started Streamlit server on port {port} for {dashboard_path}")
        else:
            stdout, stderr = process.communicate()
            error_msg = f"Streamlit process exited with code {process.returncode}"
            if stderr:
                error_msg += f": {stderr.decode()}"
            raise RuntimeError(error_msg)

        return process
    except Exception as e:
        logger.error(f"Failed to start Streamlit server: {e}")
        raise


def discover_dashboard_files(dashboards_dir: str = "app/dashboards") -> List[Path]:
    """
    Discover all Streamlit dashboard files in the dashboards directory.

    Args:
        dashboards_dir: Path to the dashboards directory

    Returns:
        List of paths to dashboard files
    """
    dashboards_path = Path(dashboards_dir).resolve()

    if not dashboards_path.exists():
        logger.warning(f"Dashboards directory not found: {dashboards_dir}")
        return []

    # Find all Python files that could be dashboards (exclude __init__, utilities, etc.)
    dashboard_files = []
    excluded_files = {"__init__.py",
                      "utilities.py", "streamlit_integration.py"}

    for file_path in dashboards_path.glob("*.py"):
        if file_path.name not in excluded_files:
            dashboard_files.append(file_path)

    logger.info(
        f"Discovered {len(dashboard_files)} dashboard files in {dashboards_dir}")
    return dashboard_files


def mount_streamlit_app(app: FastAPI, dashboard_path: str, mount_path: str = "/dashboard", port: int = 8501, dashboard_name: str = None):
    """
    Mount a Streamlit app to a FastAPI application.
    Creates an iframe endpoint that embeds the Streamlit app.

    Args:
        app: FastAPI application instance
        dashboard_path: Path to the Streamlit dashboard script
        mount_path: URL path to mount the dashboard in FastAPI
        port: Port to run Streamlit on
        dashboard_name: Human-readable name for the dashboard
    """
    # Convert to absolute path
    script_path = Path(dashboard_path).resolve()

    if not script_path.exists():
        logger.warning(f"Dashboard file not found: {dashboard_path}")
        return app

    # Generate dashboard name if not provided
    if dashboard_name is None:
        dashboard_name = script_path.stem.replace("_", " ").title()

    # Store the path and port for later use
    app.state.streamlit_dashboard_path = str(script_path)
    app.state.streamlit_mount_path = mount_path
    app.state.streamlit_port = port

    # Register dashboard
    _mounted_dashboards[mount_path] = {
        "name": dashboard_name,
        "path": str(script_path),
        "mount_path": mount_path,
        "port": port,
        "status": "registered"
    }

    # Add an iframe endpoint
    @app.get(mount_path, response_class=HTMLResponse)
    async def streamlit_dashboard():
        """Serve the Streamlit dashboard via iframe"""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{dashboard_name}</title>
            <style>
                body, html {{
                    margin: 0;
                    padding: 0;
                    width: 100%;
                    height: 100%;
                }}
                iframe {{
                    width: 100%;
                    height: 100vh;
                    border: none;
                }}
            </style>
        </head>
        <body>
            <iframe src="http://localhost:{port}"></iframe>
        </body>
        </html>
        """
        return html_content

    # Start Streamlit server in a separate thread
    def start_server():
        try:
            start_streamlit_server(str(script_path), port)
            _mounted_dashboards[mount_path]["status"] = "running"
            logger.info(f"Streamlit server started for {dashboard_name}")
        except Exception as e:
            _mounted_dashboards[mount_path]["status"] = "error"
            logger.error(
                f"Error starting Streamlit server for {dashboard_name}: {e}")

    thread = threading.Thread(target=start_server, daemon=True)
    thread.start()

    logger.info(
        f"Mounted Streamlit dashboard '{dashboard_name}' at {mount_path} from {dashboard_path} on port {port}")
    return app


def mount_all_dashboards(app: FastAPI, dashboards_dir: str = "app/dashboards", base_port: int = 8501):
    """
    Automatically discover and mount all dashboard files in the dashboards directory.

    Args:
        app: FastAPI application instance
        dashboards_dir: Path to the dashboards directory
        base_port: Starting port number for dashboards (will increment for each dashboard)

    Returns:
        FastAPI app with all dashboards mounted
    """
    dashboard_files = discover_dashboard_files(dashboards_dir)

    if not dashboard_files:
        logger.warning("No dashboard files found to mount")
        return app

    # Add endpoint to list all available dashboards
    @app.get("/dashboards", response_class=JSONResponse)
    async def list_dashboards():
        """List all available dashboards"""
        return {
            "dashboards": list(_mounted_dashboards.values()),
            "count": len(_mounted_dashboards)
        }

    # Mount each dashboard with a unique port and path
    current_port = base_port
    for dashboard_file in dashboard_files:
        dashboard_name = dashboard_file.stem.replace("_", " ").title()
        mount_path = f"/dashboard/{dashboard_file.stem}"

        try:
            mount_streamlit_app(
                app=app,
                dashboard_path=str(dashboard_file),
                mount_path=mount_path,
                port=current_port,
                dashboard_name=dashboard_name
            )
            current_port += 1
        except Exception as e:
            logger.error(
                f"Failed to mount dashboard {dashboard_file.name}: {e}")

    logger.info(
        f"Mounted {len([d for d in _mounted_dashboards.values()])} dashboards")
    return app
