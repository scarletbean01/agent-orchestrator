"""Configuration command implementation."""

import sys
from pathlib import Path

# Ensure proper imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from cli.core.config import OrchestratorConfig


def config_init_command():
    """Initialize a default configuration file."""
    config_path = Path(".orchestra/config.json")

    if config_path.exists():
        response = input(
            f"Config file already exists at {config_path}. Overwrite? (y/N): "
        )
        if response.lower() != "y":
            print("Cancelled.")
            return

    config = OrchestratorConfig.create_default()
    print(f"Created default configuration at {config_path}")
    print("\nDefault settings:")
    print(f"  archive.enabled: {config.archive.enabled}")
    print(
        f"  archive.max_completed_age_days: {config.archive.max_completed_age_days}"
    )
    print(f"  archive.max_failed_age_days: {config.archive.max_failed_age_days}")
    print(f"  archive.max_queue_size: {config.archive.max_queue_size}")
    print(f"  archive.archive_dir: {config.archive.archive_dir}")


def config_show_command():
    """Show current configuration."""
    config = OrchestratorConfig.load()
    print("\nCurrent Configuration:")
    print(f"  archive.enabled: {config.archive.enabled}")
    print(
        f"  archive.max_completed_age_days: {config.archive.max_completed_age_days}"
    )
    print(f"  archive.max_failed_age_days: {config.archive.max_failed_age_days}")
    print(f"  archive.max_queue_size: {config.archive.max_queue_size}")
    print(f"  archive.archive_dir: {config.archive.archive_dir}")


def config_set_command(key: str, value: str):
    """Set a configuration value."""
    config = OrchestratorConfig.load()

    # Parse the key path
    parts = key.split(".")
    if len(parts) != 2 or parts[0] != "archive":
        print(f"Error: Invalid key '{key}'")
        print("Valid keys: archive.enabled, archive.max_completed_age_days, etc.")
        return

    attr = parts[1]

    # Validate and set the value
    if attr == "enabled":
        if value.lower() in ("true", "1", "yes"):
            config.archive.enabled = True
        elif value.lower() in ("false", "0", "no"):
            config.archive.enabled = False
        else:
            print(f"Error: Invalid boolean value '{value}'")
            return
    elif attr in ("max_completed_age_days", "max_failed_age_days", "max_queue_size"):
        try:
            setattr(config.archive, attr, int(value))
        except ValueError:
            print(f"Error: Invalid integer value '{value}'")
            return
    elif attr == "archive_dir":
        config.archive.archive_dir = value
    else:
        print(f"Error: Unknown key '{key}'")
        return

    # Save the updated config
    config.save()
    print(f"Set {key} = {value}")
    print(f"Configuration saved to .orchestra/config.json")

