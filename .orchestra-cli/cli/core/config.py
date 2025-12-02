"""Configuration management for the orchestrator."""

import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

# Ensure proper imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


@dataclass
class ArchiveConfig:
    """Task archival settings."""

    enabled: bool = False
    max_completed_age_days: int = 7
    max_failed_age_days: int = 14
    max_queue_size: int = 100
    archive_dir: str = ".orchestra/archive"

    @classmethod
    def from_dict(cls, data: dict) -> "ArchiveConfig":
        """Create from dictionary."""
        return cls(
            enabled=data.get("enabled", False),
            max_completed_age_days=data.get("max_completed_age_days", 7),
            max_failed_age_days=data.get("max_failed_age_days", 14),
            max_queue_size=data.get("max_queue_size", 100),
            archive_dir=data.get("archive_dir", ".orchestra/archive"),
        )

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "enabled": self.enabled,
            "max_completed_age_days": self.max_completed_age_days,
            "max_failed_age_days": self.max_failed_age_days,
            "max_queue_size": self.max_queue_size,
            "archive_dir": self.archive_dir,
        }


@dataclass
class OrchestratorConfig:
    """Main configuration."""

    archive: ArchiveConfig = field(default_factory=ArchiveConfig)

    @classmethod
    def load(cls, path: Optional[Path] = None) -> "OrchestratorConfig":
        """Load config from file or use defaults."""
        config_path = path or Path(".orchestra/config.json")
        if config_path.exists():
            try:
                with open(config_path) as f:
                    data = json.load(f)
                    return cls(
                        archive=ArchiveConfig.from_dict(data.get("archive", {}))
                    )
            except Exception as e:
                print(f"Warning: Failed to load config from {config_path}: {e}")
                print("Using default configuration")
        return cls()

    def save(self, path: Optional[Path] = None):
        """Save config to file."""
        config_path = path or Path(".orchestra/config.json")
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, "w") as f:
            json.dump({"archive": self.archive.to_dict()}, f, indent=2)

    @classmethod
    def create_default(cls, path: Optional[Path] = None) -> "OrchestratorConfig":
        """Create and save a default configuration file."""
        config = cls()
        config.save(path)
        return config

