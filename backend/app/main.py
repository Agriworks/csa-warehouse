from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints.pipelines.pipeline import run_router
from app.api.endpoints.datasets.datasets import datasets_router
from app.api.endpoints.datasets.manage import manage_router
from app.api.endpoints.datasets.dataset_info import dataset_info_router
from app.api.endpoints.users.users import router as user_router
from app.api.endpoints.users.role_check import router as role_check_router
from app.auth.token_middleware import TokenAuthMiddleware
from app.auth.security import require_bearer_token
from app.dashboards.streamlit_integration import mount_all_dashboards
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Attach middleware that extracts external_id from Bearer token
app.add_middleware(TokenAuthMiddleware)

# Include routers; protect selected routers with Bearer auth dependency
app.include_router(run_router, dependencies=[Depends(require_bearer_token)])
app.include_router(datasets_router, dependencies=[
                   Depends(require_bearer_token)])
app.include_router(manage_router, dependencies=[Depends(require_bearer_token)])
app.include_router(dataset_info_router, dependencies=[
                   Depends(require_bearer_token)])
app.include_router(user_router)
app.include_router(role_check_router, dependencies=[
                   Depends(require_bearer_token)])

# Mount all Streamlit dashboards
try:
    mount_all_dashboards(
        app=app, dashboards_dir="app/dashboards", base_port=8501)
except Exception as e:
    logging.error(f"Failed to mount Streamlit dashboards: {e}")
