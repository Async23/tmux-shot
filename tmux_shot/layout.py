"""Text layout engine: lines, cells, and canvas dimensions."""

from __future__ import annotations

import unicodedata
from dataclasses import dataclass

from tmux_shot.ansi import Style, StyledSpan

DEFAULT_TAB_WIDTH = 8


@dataclass
class Cell:
    """A single character cell in the layout grid."""

    char: str
    style: Style
    display_width: int  # 1 for ASCII, 2 for CJK


@dataclass
class LayoutLine:
    """A laid-out line of character cells."""

    cells: list[Cell]
    total_width: int  # sum of display_width values


@dataclass
class LayoutResult:
    """Complete layout of all lines."""

    lines: list[LayoutLine]
    max_width: int  # widest line in cell units
    total_lines: int


def char_display_width(c: str) -> int:
    """Terminal display width: full-width/wide chars return 2, others return 1."""
    return 2 if unicodedata.east_asian_width(c) in ("F", "W") else 1


def compute(
    spans: list[StyledSpan], tab_width: int = DEFAULT_TAB_WIDTH
) -> LayoutResult:
    """Convert styled spans into a grid layout.

    Splits spans by newline, expands tabs, computes character widths.
    """
    lines: list[LayoutLine] = []
    current_cells: list[Cell] = []
    current_width = 0

    for span in spans:
        text = span.text.expandtabs(tab_width)
        for char in text:
            if char == "\n":
                lines.append(
                    LayoutLine(cells=current_cells, total_width=current_width)
                )
                current_cells = []
                current_width = 0
            elif char == "\r":
                continue  # skip carriage returns
            else:
                w = char_display_width(char)
                current_cells.append(
                    Cell(char=char, style=span.style, display_width=w)
                )
                current_width += w

    # Don't forget the last line
    lines.append(LayoutLine(cells=current_cells, total_width=current_width))

    # Strip trailing empty lines
    while len(lines) > 1 and not lines[-1].cells:
        lines.pop()

    # Ensure at least one line
    if not lines:
        lines = [LayoutLine(cells=[], total_width=0)]

    max_width = max(line.total_width for line in lines) if lines else 0

    return LayoutResult(
        lines=lines,
        max_width=max_width,
        total_lines=len(lines),
    )
