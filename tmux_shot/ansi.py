"""ANSI SGR escape sequence parser."""

from __future__ import annotations

import re
from dataclasses import dataclass

from tmux_shot.themes import Color, color_from_256, ONE_HALF_DARK

# Strip non-SGR escape sequences (CSI non-m, OSC, charset selection)
_NON_SGR_ESCAPE_RE = re.compile(
    r"\x1b(?:"
    r"\[[^m]*[a-ln-zA-Z]"              # CSI with final byte other than 'm'
    r"|\][^\x07\x1b]*(?:\x07|\x1b\\)"  # OSC sequences
    r"|\([AB012]"                       # charset selection
    r")"
)

# Split text on SGR sequences, keeping the delimiters
_SGR_RE = re.compile(r"(\x1b\[[\d;]*m)")


@dataclass
class Style:
    """Text style attributes from ANSI SGR codes."""

    fg: Color | None = None
    bg: Color | None = None
    bold: bool = False
    dim: bool = False
    italic: bool = False
    underline: bool = False
    strikethrough: bool = False
    reverse: bool = False

    def copy(self) -> Style:
        return Style(
            fg=self.fg,
            bg=self.bg,
            bold=self.bold,
            dim=self.dim,
            italic=self.italic,
            underline=self.underline,
            strikethrough=self.strikethrough,
            reverse=self.reverse,
        )


@dataclass
class StyledSpan:
    """A text segment with associated style."""

    text: str
    style: Style


def parse(text: str, palette: tuple[Color, ...] | None = None) -> list[StyledSpan]:
    """Parse text containing ANSI escape sequences into styled spans.

    Args:
        text: Raw text potentially containing ANSI escape sequences.
        palette: 16-color palette for resolving standard/256 colors.
                 Defaults to One Half Dark palette.

    Returns:
        List of StyledSpan with escape codes removed and styles applied.
    """
    if palette is None:
        palette = ONE_HALF_DARK.palette

    # Strip non-SGR escape sequences first
    text = _NON_SGR_ESCAPE_RE.sub("", text)

    # Split on SGR sequences, keeping delimiters
    parts = _SGR_RE.split(text)

    spans: list[StyledSpan] = []
    style = Style()

    for part in parts:
        if not part:
            continue

        # Check if this part is an SGR sequence
        m = re.fullmatch(r"\x1b\[([\d;]*)m", part)
        if m:
            style = _apply_sgr(style, m.group(1), palette)
        elif part:
            spans.append(StyledSpan(text=part, style=style.copy()))

    return spans


def _apply_sgr(
    style: Style, params_str: str, palette: tuple[Color, ...]
) -> Style:
    """Apply SGR parameters to a style."""
    style = style.copy()

    if not params_str:
        return Style()  # ESC[m = reset

    params = [int(p) if p else 0 for p in params_str.split(";")]
    i = 0
    while i < len(params):
        code = params[i]

        if code == 0:
            style = Style()
        elif code == 1:
            style.bold = True
        elif code == 2:
            style.dim = True
        elif code == 3:
            style.italic = True
        elif code == 4:
            style.underline = True
        elif code == 7:
            style.reverse = True
        elif code == 9:
            style.strikethrough = True
        elif code == 22:
            style.bold = False
            style.dim = False
        elif code == 23:
            style.italic = False
        elif code == 24:
            style.underline = False
        elif code == 27:
            style.reverse = False
        elif code == 29:
            style.strikethrough = False
        # Standard foreground (30-37)
        elif 30 <= code <= 37:
            style.fg = palette[code - 30]
        elif code == 38:
            color, skip = _parse_extended_color(params, i, palette)
            if color is not None:
                style.fg = color
            i += skip
        elif code == 39:
            style.fg = None
        # Standard background (40-47)
        elif 40 <= code <= 47:
            style.bg = palette[code - 40]
        elif code == 48:
            color, skip = _parse_extended_color(params, i, palette)
            if color is not None:
                style.bg = color
            i += skip
        elif code == 49:
            style.bg = None
        # Bright foreground (90-97)
        elif 90 <= code <= 97:
            style.fg = palette[8 + code - 90]
        # Bright background (100-107)
        elif 100 <= code <= 107:
            style.bg = palette[8 + code - 100]

        i += 1

    return style


def _parse_extended_color(
    params: list[int], i: int, palette: tuple[Color, ...]
) -> tuple[Color | None, int]:
    """Parse extended color after code 38 or 48.

    Returns (color, number_of_extra_params_consumed).
    """
    if i + 1 >= len(params):
        return None, 0

    mode = params[i + 1]
    if mode == 5 and i + 2 < len(params):
        # 256-color mode
        return color_from_256(params[i + 2], palette), 2
    elif mode == 2 and i + 4 < len(params):
        # 24-bit truecolor
        r = max(0, min(255, params[i + 2]))
        g = max(0, min(255, params[i + 3]))
        b = max(0, min(255, params[i + 4]))
        return (r, g, b), 4

    return None, 0
