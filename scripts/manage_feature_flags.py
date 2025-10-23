#!/usr/bin/env python3
"""
Feature Flags Management CLI

Command-line tool for managing feature flags.

Usage:
    # List all flags
    python3 scripts/manage_feature_flags.py list

    # Enable a flag
    python3 scripts/manage_feature_flags.py set use_postgresql_backend true

    # Set percentage rollout
    python3 scripts/manage_feature_flags.py set use_postgresql_backend 50%

    # Set user-specific override
    python3 scripts/manage_feature_flags.py set-user use_postgresql_backend user123 true

    # Check a flag
    python3 scripts/manage_feature_flags.py check use_postgresql_backend
"""

import sys
import os
import argparse

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api.services.feature_flags import get_feature_flags


def cmd_list(args):
    """List all feature flags"""
    flags = get_feature_flags()
    all_flags = flags.get_all_flags()

    print("\n📋 Feature Flags")
    print("=" * 60)
    print(f"{'Flag Name':<40} {'Value':<20}")
    print("-" * 60)

    for flag_name, value in sorted(all_flags.items()):
        value_str = str(value)
        if isinstance(value, bool):
            value_str = "✅ Enabled" if value else "❌ Disabled"
        print(f"{flag_name:<40} {value_str:<20}")

    print("=" * 60)
    print(f"Total: {len(all_flags)} flags")
    print("")


def cmd_check(args):
    """Check a specific feature flag"""
    flags = get_feature_flags()
    enabled = flags.is_enabled(args.flag_name)

    print(f"\n🔍 Feature Flag: {args.flag_name}")
    print("=" * 60)
    print(f"Status: {'✅ Enabled' if enabled else '❌ Disabled'}")
    print("")


def cmd_set(args):
    """Set a feature flag value"""
    flags = get_feature_flags()

    # Parse value
    value_str = args.value.lower()

    if value_str.endswith('%'):
        # Percentage rollout
        try:
            percentage = int(value_str[:-1])
            if not 0 <= percentage <= 100:
                print(f"❌ Error: Percentage must be between 0 and 100")
                return 1

            success = flags.set_percentage(args.flag_name, percentage)
            if success:
                print(f"✅ Feature flag '{args.flag_name}' set to {percentage}% rollout")
                return 0
            else:
                print(f"❌ Failed to set feature flag '{args.flag_name}'")
                return 1

        except ValueError:
            print(f"❌ Error: Invalid percentage value '{args.value}'")
            return 1

    elif value_str in ('true', '1', 'yes', 'enabled', 'on'):
        # Enable
        success = flags.set_flag(args.flag_name, True)
        if success:
            print(f"✅ Feature flag '{args.flag_name}' enabled")
            return 0
        else:
            print(f"❌ Failed to enable feature flag '{args.flag_name}'")
            return 1

    elif value_str in ('false', '0', 'no', 'disabled', 'off'):
        # Disable
        success = flags.set_flag(args.flag_name, False)
        if success:
            print(f"✅ Feature flag '{args.flag_name}' disabled")
            return 0
        else:
            print(f"❌ Failed to disable feature flag '{args.flag_name}'")
            return 1

    else:
        print(f"❌ Error: Invalid value '{args.value}'. Use: true/false or percentage (e.g., 50%)")
        return 1


def cmd_set_user(args):
    """Set a user-specific feature flag override"""
    flags = get_feature_flags()

    # Parse value
    value_str = args.value.lower()
    enabled = value_str in ('true', '1', 'yes', 'enabled', 'on')

    success = flags.set_user_override(args.flag_name, args.user_id, enabled)
    if success:
        print(f"✅ Feature flag '{args.flag_name}' set to {'enabled' if enabled else 'disabled'} for user '{args.user_id}'")
        return 0
    else:
        print(f"❌ Failed to set user override for feature flag '{args.flag_name}'")
        return 1


def main():
    parser = argparse.ArgumentParser(description="Manage feature flags")
    subparsers = parser.add_subparsers(dest='command', help='Command')

    # List command
    parser_list = subparsers.add_parser('list', help='List all feature flags')
    parser_list.set_defaults(func=cmd_list)

    # Check command
    parser_check = subparsers.add_parser('check', help='Check a feature flag')
    parser_check.add_argument('flag_name', help='Feature flag name')
    parser_check.set_defaults(func=cmd_check)

    # Set command
    parser_set = subparsers.add_parser('set', help='Set a feature flag')
    parser_set.add_argument('flag_name', help='Feature flag name')
    parser_set.add_argument('value', help='Value (true/false or percentage like 50%)')
    parser_set.set_defaults(func=cmd_set)

    # Set-user command
    parser_set_user = subparsers.add_parser('set-user', help='Set user-specific override')
    parser_set_user.add_argument('flag_name', help='Feature flag name')
    parser_set_user.add_argument('user_id', help='User ID')
    parser_set_user.add_argument('value', help='Value (true/false)')
    parser_set_user.set_defaults(func=cmd_set_user)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
