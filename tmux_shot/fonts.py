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

# Mapping from regular font filename to variant suffixes
_VARIANT_MAP = {
    "bold": [
        ("Regular", "Bold"),
        ("regular", "bold"),
        ("-Regular.", "-Bold."),
    ],
    "italic": [
        ("Regular", "Oblique"),
        ("regular", "oblique"),
        ("-Regular.", "-Oblique."),
        ("Regular", "Italic"),
        ("regular", "italic"),
        ("-Regular.", "-Italic."),
    ],
    "bold_italic": [
        ("Regular", "BoldOblique"),
        ("regular", "boldoblique"),
        ("-Regular.", "-BoldOblique."),
        ("Regular", "BoldItalic"),
        ("regular", "bolditalic"),
        ("-Regular.", "-BoldItalic."),
    ],
}

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
    """Loaded font set with optional CJK fallback and style variants."""

    primary: ImageFont.FreeTypeFont
    bold: ImageFont.FreeTypeFont | None = None
    italic: ImageFont.FreeTypeFont | None = None
    bold_italic: ImageFont.FreeTypeFont | None = None
    cjk: ImageFont.FreeTypeFont | None = None

    def select(self, is_bold: bool, is_italic: bool) -> ImageFont.FreeTypeFont:
        """Select the appropriate font variant for the given style."""
        if is_bold and is_italic and self.bold_italic is not None:
            return self.bold_italic
        if is_bold and self.bold is not None:
            return self.bold
        if is_italic and self.italic is not None:
            return self.italic
        return self.primary


def load_fonts(font_path: str | None, font_size: int) -> FontSet:
    """Load primary font, style variants, and CJK fallback.

    Args:
        font_path: Explicit font path, or None to use defaults.
        font_size: Font size in pixels (already scaled for HiDPI).

    Returns:
        FontSet with primary, bold, italic, bold_italic, and optional CJK fonts.
    """
    primary, resolved_path = _load_primary(font_path, font_size)
    bold = _load_variant(resolved_path, font_size, "bold")
    italic = _load_variant(resolved_path, font_size, "italic")
    bold_italic = _load_variant(resolved_path, font_size, "bold_italic")
    cjk = _load_cjk(font_size)
    return FontSet(
        primary=primary,
        bold=bold,
        italic=italic,
        bold_italic=bold_italic,
        cjk=cjk,
    )


def _load_primary(
    font_path: str | None, size: int
) -> tuple[ImageFont.FreeTypeFont, str | None]:
    """Load the primary monospace font.

    Returns (font, resolved_path) where resolved_path is the actual file path
    used, or None if the default bitmap font was loaded.
    """
    if font_path:
        try:
            return ImageFont.truetype(font_path, size), font_path
        except OSError:
            print(
                f"tmux-shot: warning: font not found: {font_path}",
                file=sys.stderr,
            )

    for path in _DEFAULT_FONTS:
        try:
            return ImageFont.truetype(path, size), path
        except OSError:
            continue

    print(
        "tmux-shot: warning: no monospace font found, using default",
        file=sys.stderr,
    )
    return ImageFont.load_default(), None


def _load_variant(
    primary_path: str | None, size: int, variant: str
) -> ImageFont.FreeTypeFont | None:
    """Try to load a font variant (bold/italic/bold_italic) by deriving
    the path from the primary font path."""
    if primary_path is None:
        return None

    for old, new in _VARIANT_MAP[variant]:
        if old in primary_path:
            candidate = primary_path.replace(old, new)
            try:
                return ImageFont.truetype(candidate, size)
            except OSError:
                continue

    return None


def _load_cjk(size: int) -> ImageFont.FreeTypeFont | None:
    """Load a CJK fallback font."""
    candidates = _CJK_FONTS_MACOS if sys.platform == "darwin" else _CJK_FONTS_LINUX
    for path in candidates:
        try:
            return ImageFont.truetype(path, size, index=0)
        except OSError:
            continue
    return None
