#!/usr/bin/env python3
"""
Create Admin User Script

Creates an initial admin user for the API. Run this once during initial setup.
"""

import sys
import os
import getpass
import asyncio
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from api.services.auth_service_db import AuthServiceDB
from api.database import get_session
from api.logging_config import get_logger

logger = get_logger(__name__)


async def main():
    """Create admin user interactively"""
    # Use print for interactive prompts (user interaction, not logging)
    # But use logger for status messages
    logger.info("=" * 60)
    logger.info("AI-Studio Admin User Creation")
    logger.info("=" * 60)
    logger.info("")

    async with get_session() as session:
        auth_service = AuthServiceDB(session)

        # Check if any users exist
        existing_users = await auth_service.list_users()
        if existing_users:
            logger.warning(f"{len(existing_users)} user(s) already exist:")
            for user in existing_users:
                logger.info(f"   - {user.username}")
            logger.info("")
            proceed = input("Continue anyway? (y/N): ").lower()
            if proceed != 'y':
                logger.info("Aborted.")
                return

        logger.info("")
        logger.info("Enter admin user details:")
        logger.info("-" * 60)

        # Get username
        while True:
            username = input("Username (min 3 chars): ").strip()
            if len(username) >= 3:
                break
            logger.error("Username must be at least 3 characters")

        # Get email
        email = input("Email (optional): ").strip() or None

        # Get full name
        full_name = input("Full Name (optional): ").strip() or None

        # Get password
        while True:
            password = getpass.getpass("Password (min 8 chars): ")
            if len(password) < 8:
                logger.error("Password must be at least 8 characters")
                continue

            password_confirm = getpass.getpass("Confirm password: ")
            if password != password_confirm:
                logger.error("Passwords do not match")
                continue

            break

        logger.info("")
        logger.info("Creating user...")

        try:
            user = await auth_service.create_user(
                username=username,
                password=password,
                email=email,
                full_name=full_name
            )

            logger.info("")
            logger.info("Admin user created successfully!")
            logger.info("")
            logger.info("User Details:")
            logger.info(f"   Username: {user.username}")
            if user.email:
                logger.info(f"   Email: {user.email}")
            if user.full_name:
                logger.info(f"   Name: {user.full_name}")
            logger.info(f"   Created: {user.created_at}")
            logger.info("")
            logger.info("You can now login using these credentials.")
            logger.info("")

        except ValueError as e:
            logger.error(f"Error: {e}")
            sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
