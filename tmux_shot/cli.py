"""CLI entry point and argument parsing."""

from __future__ import annotations

import argparse
import sys

from tmux_shot.ansi import parse as parse_ansi
from tmux_shot.config import load_config
from tmux_shot.fonts import load_fonts
from tmux_shot.input import InputError, read_input
from tmux_shot.layout import compute as compute_layout
from tmux_shot.output import copy_to_clipboard, open_preview, save_image
from tmux_shot.renderer import render
from tmux_shot.themes import Theme, get_theme, parse_hex_color


def main() -> None:
    """Main entry point for tmux-shot CLI."""
    p = argparse.ArgumentParser(
        prog="tmux-shot",
        description="Render terminal text to PNG screenshots with ANSI color support",
    )
    p.add_argument(
        "-o", "--output",
        help="Output file path (default: /tmp/tmux-shot-<timestamp>.png)",
    )
    p.add_argument("--theme", help="Color theme: one-half-dark, one-half-light")
    p.add_argument("--font", help="Font file path")
    p.add_argument("--font-size", type=int, help="Font size in logical pixels (default: 16)")
    p.add_argument("--padding", type=int, help="Padding in logical pixels (default: 20)")
    p.add_argument("--line-height", type=float, help="Line height multiplier (default: 1.35)")
    p.add_argument("--scale", type=int, help="HiDPI scale factor (default: 2)")
    p.add_argument("--bg", help="Override background color (hex, e.g. #282c34)")
    p.add_argument("--fg", help="Override foreground color (hex, e.g. #dcdfe4)")
    p.add_argument(
        "--light", action="store_true",
        help="Use light theme (shortcut for --theme one-half-light)",
    )
    p.add_argument("--open", action="store_true", default=None, help="Open image after rendering")
    p.add_argument("--clipboard", action="store_true", default=None, help="Copy image to system clipboard")
    p.add_argument(
        "--version", action="version",
        version=f"%(prog)s {_get_version()}",
    )

    args = p.parse_args()

    # Build CLI overrides dict (only include explicitly set values)
    cli_overrides: dict = {}
    if args.theme is not None:
        cli_overrides["theme"] = args.theme
    if args.light:
        cli_overrides["theme"] = "one-half-light"
    if args.font is not None:
        cli_overrides["font"] = args.font
    if args.font_size is not None:
        cli_overrides["font_size"] = args.font_size
    if args.padding is not None:
        cli_overrides["padding"] = args.padding
    if args.line_height is not None:
        cli_overrides["line_height"] = args.line_height
    if args.scale is not None:
        cli_overrides["scale"] = args.scale
    if args.output is not None:
        cli_overrides["output"] = args.output
    if args.open is not None:
        cli_overrides["open"] = args.open
    if args.clipboard is not None:
        cli_overrides["clipboard"] = args.clipboard

    # Load merged config
    config = load_config(cli_overrides)

    # Resolve theme
    try:
        theme = get_theme(config.theme)
    except ValueError as e:
        print(f"tmux-shot: {e}", file=sys.stderr)
        sys.exit(1)

    # Override theme colors if specified via --bg/--fg
    if args.bg or args.fg:
        theme = Theme(
            name=theme.name,
            bg=parse_hex_color(args.bg) if args.bg else theme.bg,
            fg=parse_hex_color(args.fg) if args.fg else theme.fg,
            palette=theme.palette,
        )

    # Read input
    try:
        text = read_input()
    except InputError as e:
        print(f"tmux-shot: {e}", file=sys.stderr)
        sys.exit(1)

    # Parse ANSI escape sequences
    spans = parse_ansi(text, palette=theme.palette)

    # Compute layout
    layout = compute_layout(spans, tab_width=config.tab_width)

    # Load fonts (scale font size for HiDPI)
    scale = config.scale
    fonts = load_fonts(config.font, config.font_size * scale)

    # Render image
    img = render(
        layout,
        theme,
        fonts,
        padding=config.padding * scale,
        line_height=config.line_height,
        scale=scale,
    )

    # Save and output
    path = save_image(img, config.output, config.output_dir, scale)
    print(path)

    if config.clipboard:
        copy_to_clipboard(path)
    if config.open:
        open_preview(path)


def _get_version() -> str:
    try:
        from tmux_shot import __version__

        return __version__
    except ImportError:
        return "unknown"
