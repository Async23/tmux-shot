"""Output handling: file save, clipboard copy, preview open."""

from __future__ import annotations

import subprocess
import sys
from datetime import datetime
from pathlib import Path

from PIL import Image


def save_image(
    img: Image.Image, output_path: str | None, output_dir: str, scale: int
) -> str:
    """Save image to file and return the path.

    Args:
        img: Rendered PIL Image.
        output_path: Explicit output path, or None for auto-generated.
        output_dir: Directory for auto-generated filenames.
        scale: Scale factor for DPI metadata.

    Returns:
        The path the image was saved to.
    """
    if not output_path:
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        output_path = str(Path(output_dir) / f"tmux-shot-{ts}.png")

    dpi = 72 * scale
    img.save(output_path, "PNG", dpi=(dpi, dpi))
    return output_path


def copy_to_clipboard(image_path: str) -> None:
    """Copy PNG image to system clipboard."""
    if sys.platform == "darwin":
        try:
            subprocess.run(
                [
                    "osascript",
                    "-e",
                    f'set the clipboard to (read (POSIX file "{image_path}") as \u00abclass PNGf\u00bb)',
                ],
                check=False,
            )
        except FileNotFoundError:
            print("tmux-shot: warning: osascript not found", file=sys.stderr)
    else:
        try:
            subprocess.run(
                [
                    "xclip",
                    "-selection",
                    "clipboard",
                    "-t",
                    "image/png",
                    "-i",
                    image_path,
                ],
                check=True,
            )
        except (FileNotFoundError, subprocess.CalledProcessError):
            print("tmux-shot: warning: clipboard copy failed", file=sys.stderr)


def open_preview(image_path: str) -> None:
    """Open image with the default viewer."""
    if sys.platform == "darwin":
        subprocess.run(["open", image_path], check=False)
    else:
        subprocess.run(["xdg-open", image_path], check=False)
