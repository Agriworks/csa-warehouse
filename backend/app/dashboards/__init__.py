"""
Dashboards module for serving Streamlit dashboards in FastAPI.
"""

from app.dashboards.streamlit_integration import (
    mount_streamlit_app,
    mount_all_dashboards,
    discover_dashboard_files
)

__all__ = ["mount_streamlit_app",
           "mount_all_dashboards", "discover_dashboard_files"]
