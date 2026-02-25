"""Font loading and CJK fallback."""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

from PIL import ImageFont

# Default monospace font candidates
_DEFAULT_FONTS = [
    str(Path.home() / "Library/Fonts/DejaVuSansMNerdFontMono-Regular.ttf"),
    str(Path.home() / "Library/Fonts/DejaVuSansMono.ttf"),
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
]

# CJK font candidates per platform
_CJK_FONTS_MACOS = [
    "/System/Library/Fonts/Hiragino Sans GB.ttc",
    "/System/Library/Fonts/STHeiti Medium.ttc",
    "/System/Library/Fonts/Supplemental/Songti.ttc",
    "/System/Library/Fonts/PingFang.ttc",
]

_CJK_FONTS_LINUX = [
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
    "/usr/share/fonts/truetype/droid/DroidSansFallback.ttf",
]


@dataclass
class FontSet:
    """Loaded font set with optional CJK fallback."""

    primary: ImageFont.FreeTypeFont
    cjk: ImageFont.FreeTypeFont | None = None


def load_fonts(font_path: str | None, font_size: int) -> FontSet:
    """Load primary font and CJK fallback.

    Args:
        font_path: Explicit font path, or None to use defaults.
        font_size: Font size in pixels (already scaled for HiDPI).

    Returns:
        FontSet with primary and optional CJK fonts.
    """
    primary = _load_primary(font_path, font_size)
    cjk = _load_cjk(font_size)
    return FontSet(primary=primary, cjk=cjk)


def _load_primary(font_path: str | None, size: int) -> ImageFont.FreeTypeFont:
    """Load the primary monospace font."""
    if font_path:
        try:
            return ImageFont.truetype(font_path, size)
        except OSError:
            print(
                f"tmux-shot: warning: font not found: {font_path}",
                file=sys.stderr,
            )

    for path in _DEFAULT_FONTS:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue

    print(
        "tmux-shot: warning: no monospace font found, using default",
        file=sys.stderr,
    )
    return ImageFont.load_default()


def _load_cjk(size: int) -> ImageFont.FreeTypeFont | None:
    """Load a CJK fallback font."""
    candidates = _CJK_FONTS_MACOS if sys.platform == "darwin" else _CJK_FONTS_LINUX
    for path in candidates:
        try:
            return ImageFont.truetype(path, size, index=0)
        except OSError:
            continue
    return None
