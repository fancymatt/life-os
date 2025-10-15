#!/usr/bin/env python3
"""
Create Admin User Script

Creates an initial admin user for the API. Run this once during initial setup.
"""

import sys
import os
import getpass
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from api.services.auth_service import auth_service


def main():
    """Create admin user interactively"""
    print("=" * 60)
    print("AI-Studio Admin User Creation")
    print("=" * 60)
    print()

    # Check if any users exist
    existing_users = auth_service.list_users()
    if existing_users:
        print(f"⚠️  Warning: {len(existing_users)} user(s) already exist:")
        for user in existing_users:
            print(f"   - {user.username}")
        print()
        proceed = input("Continue anyway? (y/N): ").lower()
        if proceed != 'y':
            print("Aborted.")
            return

    print()
    print("Enter admin user details:")
    print("-" * 60)

    # Get username
    while True:
        username = input("Username (min 3 chars): ").strip()
        if len(username) >= 3:
            break
        print("❌ Username must be at least 3 characters")

    # Get email
    email = input("Email (optional): ").strip() or None

    # Get full name
    full_name = input("Full Name (optional): ").strip() or None

    # Get password
    while True:
        password = getpass.getpass("Password (min 8 chars): ")
        if len(password) < 8:
            print("❌ Password must be at least 8 characters")
            continue

        password_confirm = getpass.getpass("Confirm password: ")
        if password != password_confirm:
            print("❌ Passwords do not match")
            continue

        break

    print()
    print("Creating user...")

    try:
        user = auth_service.create_user(
            username=username,
            password=password,
            email=email,
            full_name=full_name
        )

        print()
        print("✅ Admin user created successfully!")
        print()
        print("User Details:")
        print(f"   Username: {user.username}")
        if user.email:
            print(f"   Email: {user.email}")
        if user.full_name:
            print(f"   Name: {user.full_name}")
        print(f"   Created: {user.created_at}")
        print()
        print("You can now login using these credentials.")
        print()

    except ValueError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
