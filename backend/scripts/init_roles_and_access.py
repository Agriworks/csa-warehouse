#!/usr/bin/env python3
"""
Script to initialize default roles and endpoint access controls.
Run this script to set up the initial roles and permissions in the database.
"""

import sys
import os
from datetime import datetime

# Add the parent directory of backend/app to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.schemas.models import Role
from app.db.crud import (
    ensure_default_role_and_get_id,
    get_role_by_name,
    create_role,
    initialize_default_endpoint_access,
)


def create_default_roles():
    """Create default roles if they don't exist."""
    roles_to_create = [
        {"role_name": "user", "description": "Default role for regular users - can view and browse data"},
        {"role_name": "admin", "description": "Administrator role - can manage data and users"},
        {"role_name": "superadmin", "description": "Super administrator role - full system access"},
    ]

    created_roles = []
    for role_data in roles_to_create:
        existing_role = get_role_by_name(role_data["role_name"])
        if not existing_role:
            role = Role(
                role_name=role_data["role_name"],
                description=role_data["description"],
                is_active=True,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )
            create_role(role)
            created_roles.append(role_data["role_name"])
            print(f"✅ Created role: {role_data['role_name']}")
        else:
            print(f"ℹ️  Role already exists: {role_data['role_name']}")

    return created_roles


def main():
    """Main function to initialize roles and endpoint access."""
    print("🚀 Initializing roles and endpoint access controls...")

    # Create default roles
    print("\n📋 Creating default roles...")
    created_roles = create_default_roles()

    # Initialize endpoint access controls
    print("\n🔐 Initializing endpoint access controls...")
    try:
        initialize_default_endpoint_access()
        print("✅ Endpoint access controls initialized successfully")
    except Exception as e:
        print(f"❌ Error initializing endpoint access controls: {e}")
        return False

    print("\n🎉 Initialization completed successfully!")
    print(f"Created {len(created_roles)} new roles: {', '.join(created_roles)}")
    print("\nDefault endpoint access rules:")
    print("- user: Can access /dashboard, /datastore/browse, /settings, /about, /support")
    print("- admin: Can access all pages including /pipeline and /usermanagement")
    print("- superadmin: Can access all pages with full permissions")

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
