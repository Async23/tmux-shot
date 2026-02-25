"""Pillow-based image renderer."""

from __future__ import annotations

from PIL import Image, ImageDraw

from tmux_shot.ansi import Style
from tmux_shot.fonts import FontSet
from tmux_shot.layout import Cell, LayoutResult
from tmux_shot.themes import Color, Theme


def render(
    layout: LayoutResult,
    theme: Theme,
    fonts: FontSet,
    *,
    padding: int,
    line_height: float,
    scale: int,
) -> Image.Image:
    """Render layout into a Pillow Image.

    Args:
        layout: Computed layout with lines and cells.
        theme: Color theme for default fg/bg and reverse colors.
        fonts: Loaded font set (primary + CJK).
        padding: Padding in scaled pixels.
        line_height: Line height multiplier.
        scale: HiDPI scale factor (used only for reference).

    Returns:
        Rendered PIL Image.
    """
    # Cell width = width of a single ASCII character
    cell_w = fonts.primary.getlength("M")

    # Line step height
    ascent, descent = fonts.primary.getmetrics()
    line_step = int((ascent + descent) * line_height)

    # Canvas dimensions
    img_w = int(cell_w * layout.max_width) + padding * 2
    img_h = line_step * layout.total_lines + padding * 2

    # Ensure minimum size
    img_w = max(img_w, padding * 2 + int(cell_w))
    img_h = max(img_h, padding * 2 + line_step)

    img = Image.new("RGB", (img_w, img_h), theme.bg)
    draw = ImageDraw.Draw(img)

    y = padding
    for line in layout.lines:
        if not line.cells:
            y += line_step
            continue
        _render_line(
            draw, line.cells, y, padding, cell_w, line_step,
            theme, fonts, ascent,
        )
        y += line_step

    return img


def _render_line(
    draw: ImageDraw.ImageDraw,
    cells: list[Cell],
    y: int,
    padding: int,
    cell_w: float,
    line_step: int,
    theme: Theme,
    fonts: FontSet,
    ascent: int,
) -> None:
    """Render cells for a single line, batching same-style ASCII runs."""
    x = float(padding)
    i = 0

    while i < len(cells):
        cell = cells[i]

        if cell.display_width == 1:
            # Batch consecutive ASCII cells with the same style
            run_text = cell.char
            j = i + 1
            while (
                j < len(cells)
                and cells[j].display_width == 1
                and cells[j].style == cell.style
            ):
                run_text += cells[j].char
                j += 1

            fg, bg = _resolve_colors(cell.style, theme)
            w = cell_w * len(run_text)

            if bg is not None:
                draw.rectangle([x, y, x + w, y + line_step], fill=bg)

            font = fonts.select(cell.style.bold, cell.style.italic)
            draw.text((x, y), run_text, font=font, fill=fg)

            _draw_decorations(draw, cell.style, x, y, w, ascent, fg)

            x += w
            i = j
        else:
            # CJK character: render individually, centered in double-width cell
            fg, bg = _resolve_colors(cell.style, theme)
            w = cell_w * 2

            if bg is not None:
                draw.rectangle([x, y, x + w, y + line_step], fill=bg)

            font = fonts.cjk if fonts.cjk is not None else fonts.primary
            glyph_w = font.getlength(cell.char)
            offset = (w - glyph_w) / 2
            draw.text((x + offset, y), cell.char, font=font, fill=fg)

            _draw_decorations(draw, cell.style, x, y, w, ascent, fg)

            x += w
            i += 1


def _resolve_colors(
    style: Style, theme: Theme
) -> tuple[Color, Color | None]:
    """Resolve style colors, handling reverse and defaults.

    Returns (fg_color, bg_color_or_none).
    bg is None when it matches the theme background (no rectangle needed).
    """
    fg = style.fg if style.fg is not None else theme.fg
    bg = style.bg  # None = theme default, no need to draw rectangle

    if style.reverse:
        fg, bg = (bg if bg is not None else theme.bg), fg

    if style.dim:
        fg = (fg[0] // 2, fg[1] // 2, fg[2] // 2)

    return fg, bg


def _draw_decorations(
    draw: ImageDraw.ImageDraw,
    style: Style,
    x: float,
    y: int,
    width: float,
    ascent: int,
    fg: Color,
) -> None:
    """Draw underline and/or strikethrough decorations."""
    if style.underline:
        uy = y + ascent + 1
        draw.line([(x, uy), (x + width, uy)], fill=fg, width=1)
    if style.strikethrough:
        sy = y + ascent * 2 // 3
        draw.line([(x, sy), (x + width, sy)], fill=fg, width=1)
