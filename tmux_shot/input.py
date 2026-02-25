"""Text input acquisition from stdin or clipboard."""

from __future__ import annotations

import subprocess
import sys


class InputError(Exception):
    """Raised when no input text is available."""


def read_input() -> str:
    """Read input text from stdin pipe or system clipboard.

    Returns:
        Raw text string (may contain ANSI escape sequences).

    Raises:
        InputError: If no content is available.
    """
    if not sys.stdin.isatty():
        text = sys.stdin.read()
    else:
        text = _read_clipboard()

    if not text or not text.strip():
        raise InputError("No content to render")

    return text


def _read_clipboard() -> str:
    """Read text from system clipboard."""
    if sys.platform == "darwin":
        cmd = ["pbpaste"]
    else:
        # Try Linux clipboard tools
        for tool in [
            ["xclip", "-selection", "clipboard", "-o"],
            ["xsel", "--clipboard", "--output"],
            ["wl-paste"],
        ]:
            try:
                return subprocess.check_output(
                    tool, text=True, stderr=subprocess.DEVNULL
                )
            except (FileNotFoundError, subprocess.CalledProcessError):
                continue
        return ""

    try:
        return subprocess.check_output(cmd, text=True)
    except (FileNotFoundError, subprocess.CalledProcessError):
        return ""
