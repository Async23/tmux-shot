"""Configuration file loading and merging."""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from pathlib import Path

from tmux_shot.themes import DEFAULT_THEME

try:
    import tomllib  # type: ignore[import-not-found]
except ModuleNotFoundError:
    try:
        import tomli as tomllib  # type: ignore[import-not-found,no-redef]
    except ModuleNotFoundError:
        tomllib = None  # type: ignore[assignment]

CONFIG_PATH = Path.home() / ".config" / "tmux-shot" / "config.toml"


@dataclass
class Config:
    """Merged configuration from all sources."""

    theme: str = DEFAULT_THEME
    font: str | None = None
    font_size: int = 16
    padding: int = 20
    line_height: float = 1.35
    scale: int = 2
    tab_width: int = 8
    output_dir: str = "/tmp"
    output: str | None = None
    clipboard: bool = False
    open: bool = False


def load_config(cli_args: dict | None = None) -> Config:
    """Load config with priority: CLI > env vars > config file > defaults."""
    config = Config()

    # Layer 1: config file
    _apply_config_file(config)

    # Layer 2: environment variables
    _apply_env_vars(config)

    # Layer 3: CLI arguments (highest priority)
    if cli_args:
        _apply_cli_args(config, cli_args)

    return config


def _apply_config_file(config: Config) -> None:
    """Read and apply TOML config file if it exists."""
    if tomllib is None or not CONFIG_PATH.exists():
        return

    try:
        with open(CONFIG_PATH, "rb") as f:
            data = tomllib.load(f)
    except Exception as e:
        print(f"tmux-shot: warning: failed to read config: {e}", file=sys.stderr)
        return

    general = data.get("general", {})
    font_sec = data.get("font", {})
    layout = data.get("layout", {})
    output = data.get("output", {})

    if "theme" in general:
        config.theme = general["theme"]
    if "scale" in general:
        config.scale = int(general["scale"])
    if "open" in general:
        config.open = bool(general["open"])

    if "family" in font_sec:
        config.font = font_sec["family"]
    if "size" in font_sec:
        config.font_size = int(font_sec["size"])
    if "line_height" in font_sec:
        config.line_height = float(font_sec["line_height"])

    if "padding" in layout:
        config.padding = int(layout["padding"])
    if "tab_width" in layout:
        config.tab_width = int(layout["tab_width"])

    if "directory" in output:
        config.output_dir = output["directory"]
    if "clipboard" in output:
        config.clipboard = bool(output["clipboard"])


def _apply_env_vars(config: Config) -> None:
    """Apply environment variable overrides."""
    env_map: dict[str, tuple[str, type]] = {
        "TMUX_SHOT_THEME": ("theme", str),
        "TMUX_SHOT_FONT": ("font", str),
        "TMUX_SHOT_FONT_SIZE": ("font_size", int),
        "TMUX_SHOT_PADDING": ("padding", int),
        "TMUX_SHOT_SCALE": ("scale", int),
        "TMUX_SHOT_OUTPUT_DIR": ("output_dir", str),
    }

    for env_key, (attr, type_fn) in env_map.items():
        value = os.environ.get(env_key)
        if value is not None:
            setattr(config, attr, type_fn(value))


def _apply_cli_args(config: Config, args: dict) -> None:
    """Apply CLI arguments (highest priority)."""
    for key, value in args.items():
        if value is not None and hasattr(config, key):
            setattr(config, key, value)
