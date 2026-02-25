"""Built-in color schemes and color utilities."""

from __future__ import annotations

from dataclasses import dataclass

Color = tuple[int, int, int]


@dataclass(frozen=True)
class Theme:
    """A terminal color theme with 16-color palette."""

    name: str
    bg: Color
    fg: Color
    palette: tuple[Color, ...]  # 16 colors: 8 standard + 8 bright


ONE_HALF_DARK = Theme(
    name="one-half-dark",
    bg=(40, 44, 52),
    fg=(220, 223, 228),
    palette=(
        (40, 44, 52),       # 0  black
        (224, 108, 117),    # 1  red
        (152, 195, 121),    # 2  green
        (229, 192, 123),    # 3  yellow
        (97, 175, 239),     # 4  blue
        (198, 120, 221),    # 5  magenta
        (86, 182, 194),     # 6  cyan
        (220, 223, 228),    # 7  white
        (92, 99, 112),      # 8  bright black
        (224, 108, 117),    # 9  bright red
        (152, 195, 121),    # 10 bright green
        (229, 192, 123),    # 11 bright yellow
        (97, 175, 239),     # 12 bright blue
        (198, 120, 221),    # 13 bright magenta
        (86, 182, 194),     # 14 bright cyan
        (220, 223, 228),    # 15 bright white
    ),
)

ONE_HALF_LIGHT = Theme(
    name="one-half-light",
    bg=(250, 250, 250),
    fg=(56, 58, 66),
    palette=(
        (56, 58, 66),       # 0  black
        (228, 86, 73),      # 1  red
        (80, 161, 79),      # 2  green
        (193, 132, 1),      # 3  yellow
        (1, 132, 188),      # 4  blue
        (166, 38, 164),     # 5  magenta
        (9, 151, 179),      # 6  cyan
        (250, 250, 250),    # 7  white
        (79, 82, 94),       # 8  bright black
        (228, 86, 73),      # 9  bright red
        (80, 161, 79),      # 10 bright green
        (193, 132, 1),      # 11 bright yellow
        (1, 132, 188),      # 12 bright blue
        (166, 38, 164),     # 13 bright magenta
        (9, 151, 179),      # 14 bright cyan
        (250, 250, 250),    # 15 bright white
    ),
)

BUILTIN_THEMES: dict[str, Theme] = {
    "one-half-dark": ONE_HALF_DARK,
    "one-half-light": ONE_HALF_LIGHT,
}

DEFAULT_THEME = "one-half-dark"


def get_theme(name: str) -> Theme:
    """Get a built-in theme by name."""
    if name not in BUILTIN_THEMES:
        available = ", ".join(BUILTIN_THEMES)
        raise ValueError(f"Unknown theme '{name}'. Available: {available}")
    return BUILTIN_THEMES[name]


def color_from_256(index: int, palette: tuple[Color, ...]) -> Color:
    """Convert a 256-color index to RGB.

    Indices 0-15 use the theme palette, 16-231 use the 6x6x6 color cube,
    232-255 use the grayscale ramp.
    """
    if 0 <= index <= 15:
        return palette[index]
    if 16 <= index <= 231:
        n = index - 16
        r = 0 if n // 36 == 0 else 55 + 40 * (n // 36)
        g = 0 if (n % 36) // 6 == 0 else 55 + 40 * ((n % 36) // 6)
        b = 0 if n % 6 == 0 else 55 + 40 * (n % 6)
        return (r, g, b)
    if 232 <= index <= 255:
        v = 8 + 10 * (index - 232)
        return (v, v, v)
    return palette[7]  # fallback to white


def parse_hex_color(value: str) -> Color:
    """Parse '#rrggbb' or 'rrggbb' to RGB tuple."""
    h = value.lstrip("#")
    if len(h) != 6:
        raise ValueError(f"Invalid hex color: {value}")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))
