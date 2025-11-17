"""
Settings manager for Download App.
Handles loading/saving user preferences (downloads folder, dark mode, window size, etc.).
"""
import json
from pathlib import Path
from typing import Optional, Dict, Any


class SettingsManager:
    """Load and save application settings to a JSON file."""

    def __init__(self, config_dir: Optional[Path] = None):
        """Initialize settings manager.
        
        Args:
            config_dir: Directory to store settings.json. Defaults to user's config directory.
        """
        if config_dir is None:
            # Use platform-specific config directory
            if Path.home().name:
                # Windows: %APPDATA%/download-app, macOS/Linux: ~/.config/download-app
                if Path.home().drive:  # Windows
                    config_dir = Path.home() / "AppData" / "Local" / "download-app"
                else:  # Unix-like
                    config_dir = Path.home() / ".config" / "download-app"
            else:
                config_dir = Path.cwd() / ".config"

        self.config_dir = Path(config_dir)
        self.config_file = self.config_dir / "settings.json"
        self.config_dir.mkdir(parents=True, exist_ok=True)

    def load(self) -> Dict[str, Any]:
        """Load settings from file. Return defaults if file doesn't exist."""
        if self.config_file.exists():
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        return self._default_settings()

    def save(self, settings: Dict[str, Any]) -> None:
        """Save settings to file."""
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Failed to save settings: {e}")

    def _default_settings(self) -> Dict[str, Any]:
        """Return default settings."""
        default_downloads = Path.cwd().parent / "downloads"
        return {
            "downloads_dir": str(default_downloads),
            "dark_mode": False,
            "window_width": 700,
            "window_height": 280,
            "window_x": 100,
            "window_y": 100,
            "language": "vi",  # Default to Vietnamese
        }

    def get(self, key: str, default: Any = None) -> Any:
        """Get a setting value by key."""
        settings = self.load()
        return settings.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set a setting value and save to file."""
        settings = self.load()
        settings[key] = value
        self.save(settings)

    def update(self, updates: Dict[str, Any]) -> None:
        """Update multiple settings and save to file."""
        settings = self.load()
        settings.update(updates)
        self.save(settings)
