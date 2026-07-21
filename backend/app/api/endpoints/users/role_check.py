from fastapi import APIRouter, HTTPException, Depends, Header, Request
import logging
import requests
from typing import Optional
import re
from app.schemas.models import RoleCheckRequest, RoleCheckResponse
from app.db.crud import (
    get_user_by_external_id,
    get_role_by_name,
    get_endpoint_access_by_role_and_endpoint,
    initialize_default_endpoint_access,
    get_role_by_id,
)

router = APIRouter()
logger = logging.getLogger(__name__)


def extract_user_id_from_token(authorization: str) -> str:
    """
    Extract user ID (OIDC subject `sub`) using Google's standard OpenID Connect
    UserInfo endpoint with the provided OAuth2 access token.
    """
    if not authorization or not authorization.startswith("Bearer "):
        logger.warning("Missing or invalid Authorization header while extracting user id")
        raise HTTPException(status_code=401, detail="Invalid authorization header")

    # Extract token from authorization header
    token = authorization.split(" ")[1]
    try:
        resp = requests.get(
            "https://www.googleapis.com/oauth2/v3/userinfo",
            headers={"Authorization": f"Bearer {token}"},
            timeout=5,
        )
        if resp.status_code == 200:
            data = resp.json()
            sub = data.get("sub")
            if isinstance(sub, str) and sub:
                logger.debug("Extracted sub from Google UserInfo")
                return sub
            logger.error("Google UserInfo response missing sub: %s", data)
        else:
            logger.error("Google UserInfo request failed: %s %s", resp.status_code, resp.text)
    except Exception as e:
        logger.exception("Error calling Google UserInfo: %s", e)
    # If we cannot resolve sub, treat as invalid token
    raise HTTPException(status_code=401, detail="Invalid access token")


def find_matching_endpoint_access(role: str, path: str):
    """
    Find the most specific endpoint access rule that matches the given path.
    """
    # Get all endpoint access rules for the role
    from app.db.database import endpoint_access_collection

    all_access = list(endpoint_access_collection.find({"role": role}))

    if not all_access:
        return None

    # Sort by endpoint specificity (longer paths are more specific)
    sorted_access = sorted(all_access, key=lambda x: len(x.get("endpoint", "")), reverse=True)

    # Find the first matching endpoint
    for access in sorted_access:
        endpoint_pattern = access.get("endpoint", "")
        if path.startswith(endpoint_pattern):
            return access

    return None


@router.post("/users/role-check", response_model=RoleCheckResponse)
def check_user_role_access(request: RoleCheckRequest, fastapi_request: Request, authorization: str = Header(None)):
    """
    Check if the current user has access to the requested path based on their role.
    """
    try:
        logger.info("Role check requested: path=%s", getattr(request, "path", None))
        # Initialize default endpoint access if not exists
        initialize_default_endpoint_access()

        # Extract external_id from middleware if available; fallback to header
        external_id = getattr(fastapi_request.state, "external_id", None)
        if not external_id:
            external_id = extract_user_id_from_token(authorization)
        logger.debug("Resolved external_id for role check: %s", external_id)

        # Get user from database
        user = get_user_by_external_id(external_id)
        if not user:
            logger.warning("User not found for external_id=%s", external_id)
            raise HTTPException(status_code=404, detail="User not found")

        # Get user's role
        role_ids = user.get("role_id")
        role_name = "user"
        if role_ids:
            # Handle both list of IDs and single ID cases
            if not isinstance(role_ids, list):
                role_ids = [role_ids]
            
            roles_found = []
            for r_id in role_ids:
                role = get_role_by_id(r_id)
                if role and role.get("role_name"):
                    roles_found.append(role["role_name"])
            
            # Select the most privileged role if multiple exist
            if "superadmin" in roles_found:
                role_name = "superadmin"
            elif "admin" in roles_found:
                role_name = "admin"
            elif roles_found:
                role_name = roles_found[0]
        logger.debug("User role resolved: role_ids=%s role_name=%s", role_ids, role_name)

        # Find matching endpoint access rule
        endpoint_access = find_matching_endpoint_access(role_name, request.path)
        logger.debug("Matched endpoint access: %s", endpoint_access)

        if not endpoint_access:
            # No access rule found, deny access
            logger.info("No endpoint access rule found: role=%s path=%s", role_name, request.path)
            return RoleCheckResponse(viewer=False, contributor=False, admin=False, role_name=role_name)

        return RoleCheckResponse(
            viewer=endpoint_access.get("viewer", False),
            contributor=endpoint_access.get("contributor", False),
            admin=endpoint_access.get("admin", False),
            role_name=role_name,
        )

    except HTTPException as http_exc:
        logger.warning("HTTPException during role check: status=%s detail=%s", http_exc.status_code, http_exc.detail)
        raise
    except Exception as e:
        logger.exception("Unhandled error during role check for path=%s", getattr(request, "path", None))
        raise HTTPException(status_code=500, detail=f"Error checking role access: {str(e)}")


@router.get("/users/role-check/init")
def initialize_endpoint_access():
    """
    Initialize default endpoint access controls.
    This endpoint can be called to set up the default access rules.
    """
    try:
        initialize_default_endpoint_access()
        return {"message": "Default endpoint access controls initialized successfully"}
    except Exception as e:
        logger.exception("Failed to initialize default endpoint access")
        raise HTTPException(status_code=500, detail=f"Error initializing endpoint access: {str(e)}")
