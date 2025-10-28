# Streamlit Dashboards Module

This module provides integration between Streamlit dashboards and the FastAPI backend.

## Usage

Dashboards are **automatically discovered and mounted** when the FastAPI application starts. Any Python file in the `dashboards/` directory (excluding `__init__.py`, `utilities.py`, and `streamlit_integration.py`) will be mounted as a dashboard.

### Accessing Dashboards

- **Dashboard listing**: `http://localhost:8000/dashboards` - JSON API to list all available dashboards
- **Individual dashboards**: `http://localhost:8000/dashboard/{filename_without_extension}`
  - Example: `demo_dashboard.py` → `http://localhost:8000/dashboard/demo_dashboard`
- **Direct Streamlit access**: Each dashboard runs on a separate port starting from 8501

### Example

For the demo dashboard:
- **FastAPI endpoint**: `http://localhost:8000/dashboard/demo_dashboard`
- **Direct Streamlit**: `http://localhost:8501`

## Adding New Dashboards

Simply create a new Streamlit dashboard file in the `dashboards/` directory! The system will automatically:

1. Discover the new dashboard file
2. Assign it a unique port (auto-incrementing from the base port)
3. Create a mount path based on the filename
4. Register it in the dashboard listing

### Example: Creating a New Dashboard

```python
# File: app/dashboards/sales_dashboard.py
import streamlit as st

st.title("Sales Dashboard")
# ... your dashboard code ...
```

This dashboard will automatically be mounted at:
- **URL**: `http://localhost:8000/dashboard/sales_dashboard`
- **Port**: Automatically assigned (8502, 8503, etc.)

### Manual Mounting (Optional)

If you need manual control over a specific dashboard:

```python
from app.dashboards.streamlit_integration import mount_streamlit_app

mount_streamlit_app(
    app=app,
    dashboard_path="app/dashboards/your_dashboard.py",
    mount_path="/custom-route",
    port=8601,  # Specific port
    dashboard_name="Custom Dashboard Name"
)
```

## Demo Dashboard

The demo dashboard (`demo_dashboard.py`) demonstrates:
- Data visualization with charts and graphs
- Interactive widgets and controls
- Metric displays
- Date range filtering
- Data export functionality

## Architecture

The integration runs Streamlit as a subprocess and embeds it in FastAPI using an iframe. This approach allows:
- Multiple Streamlit dashboards to run on different ports
- FastAPI to continue serving its API endpoints
- Dashboards to maintain their interactive features
- Automatic discovery and mounting of new dashboards

### Key Functions

- `discover_dashboard_files()` - Scans the dashboards directory for Python files
- `mount_streamlit_app()` - Mounts a single dashboard (used internally)
- `mount_all_dashboards()` - Automatically discovers and mounts all dashboards

## Dashboard Registry

All mounted dashboards are registered in a global registry that tracks:
- Dashboard name (human-readable)
- File path
- Mount path (URL endpoint)
- Port number
- Status (registered, running, error)

Access the registry via the `/dashboards` endpoint.

## Notes

- Ensure Streamlit is installed: `pip install streamlit`
- Each dashboard runs on a separate port (auto-incremented)
- Excluded files: `__init__.py`, `utilities.py`, `streamlit_integration.py`
- For production deployments, consider running Streamlit as a separate service
