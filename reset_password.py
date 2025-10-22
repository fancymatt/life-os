#!/usr/bin/env python3
"""
Password Reset Script

Resets a user's password in the AI-Studio system.
Usage: python reset_password.py <username> <new_password>
"""

import sys
import json
from pathlib import Path
from passlib.context import CryptContext
from datetime import datetime

def truncate_password(password: str) -> str:
    """
    Truncate password to 72 bytes for bcrypt compatibility

    Bcrypt has a maximum password length of 72 bytes.
    """
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        truncated_bytes = password_bytes[:72]
        return truncated_bytes.decode('utf-8', errors='ignore')
    return password

def reset_password(username: str, new_password: str):
    """Reset a user's password"""
    # Setup password hashing
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    # Load users file
    users_file = Path(__file__).parent / "data" / "users.json"

    if not users_file.exists():
        print(f"❌ Error: users file not found at {users_file}")
        return False

    try:
        users = json.loads(users_file.read_text())
    except json.JSONDecodeError as e:
        print(f"❌ Error: Failed to parse users.json: {e}")
        return False

    # Check if user exists
    if username not in users:
        print(f"❌ Error: User '{username}' not found")
        print(f"   Available users: {', '.join(users.keys())}")
        return False

    # Truncate password if necessary (bcrypt has 72 byte limit)
    new_password = truncate_password(new_password)

    # Hash the new password
    hashed_password = pwd_context.hash(new_password)

    # Update user's password
    users[username]["hashed_password"] = hashed_password
    users[username]["last_login"] = None  # Reset last login

    # Save updated users file
    try:
        users_file.write_text(json.dumps(users, indent=2))
        print(f"✅ Password reset successful for user '{username}'")
        print(f"   New password: {new_password}")
        print(f"   Hash: {hashed_password[:50]}...")
        return True
    except Exception as e:
        print(f"❌ Error: Failed to save users.json: {e}")
        return False

def main():
    if len(sys.argv) != 3:
        print("Usage: python reset_password.py <username> <new_password>")
        print("\nExample:")
        print("  python reset_password.py fancymatt mynewpassword123")
        sys.exit(1)

    username = sys.argv[1]
    new_password = sys.argv[2]

    print(f"🔐 Resetting password for user: {username}")
    print(f"   New password: {new_password}")
    print()

    if reset_password(username, new_password):
        print()
        print("🎉 Success! You can now login with your new password.")
        print("   1. Open http://localhost:3000")
        print(f"   2. Login with username: {username}")
        print(f"   3. Use the new password you just set")
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
