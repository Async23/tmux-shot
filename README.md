# tmux-shot

Render terminal text to beautiful PNG screenshots with full ANSI color support. Built for tmux users who need to share long terminal output as a single image.

## Features

- **ANSI Color Rendering** -- Faithfully renders 8/16/256/truecolor ANSI escape sequences including bold, dim, italic, underline, strikethrough, and reverse
- **CJK Support** -- Correct double-width character alignment with automatic CJK font fallback
- **Retina / HiDPI** -- Default 2x rendering; macOS Preview displays at correct logical size
- **Themes** -- Built-in One Half Dark and One Half Light color schemes, with `--bg`/`--fg` overrides
- **tmux Integration** -- One-key screenshot via `copy-pipe` binding in tmux copy-mode
- **Flexible Input** -- Reads from stdin pipe or system clipboard automatically
- **Clipboard Output** -- Copy the rendered PNG directly to the system clipboard
- **Config File** -- Persistent preferences via `~/.config/tmux-shot/config.toml`
- **Cross-Platform** -- macOS (primary) and Linux support

## Installation

**Requires Python 3.10+ and [Pillow](https://pillow.readthedocs.io/).**

```bash
# From PyPI
pip install tmux-shot

# Or with pipx (isolated environment)
pipx install tmux-shot

# From source
git clone https://github.com/<user>/tmux-shot.git
cd tmux-shot
pip install -e .
```

## Quick Start

```bash
# Screenshot from clipboard, open in Preview
tmux-shot --open

# Pipe any command output
ls --color=always | tmux-shot --open

# Light theme + copy to clipboard
echo "hello world" | tmux-shot --light --clipboard
```

## tmux Integration

Add to `~/.tmux.conf`:

```tmux
# Press Y in copy-mode to screenshot the selection and open it
bind -T copy-mode-vi Y send-keys -X copy-pipe-and-cancel "tmux-shot --open --clipboard"
```

Reload tmux config (`tmux source ~/.tmux.conf`), then:

1. Enter copy-mode: `prefix + [`
2. Select text with `v` and movement keys
3. Press `Y` -- a PNG screenshot is generated, copied to clipboard, and opened in Preview

### Capture Current Pane

```bash
# Capture visible pane content
tmux capture-pane -p -e | tmux-shot --open

# Capture with scrollback (last 500 lines)
tmux capture-pane -p -e -S -500 | tmux-shot --open
```

> **Note:** Use `-e` flag with `tmux capture-pane` to preserve ANSI escape sequences.

## CLI Reference

| Option | Default | Description |
|--------|---------|-------------|
| `-o, --output PATH` | `/tmp/tmux-shot-<timestamp>.png` | Output file path |
| `--theme NAME` | `one-half-dark` | Color theme (`one-half-dark`, `one-half-light`) |
| `--light` | | Shortcut for `--theme one-half-light` |
| `--font PATH` | Auto-detected | Path to a monospace `.ttf`/`.otf` font file |
| `--font-size N` | `16` | Font size in logical pixels |
| `--padding N` | `20` | Image padding in logical pixels |
| `--line-height F` | `1.35` | Line height multiplier |
| `--scale N` | `2` | HiDPI scale factor (2 = Retina) |
| `--bg COLOR` | Theme default | Override background color (`#rrggbb`) |
| `--fg COLOR` | Theme default | Override foreground color (`#rrggbb`) |
| `--open` | `false` | Open image in default viewer after rendering |
| `--clipboard` | `false` | Copy image to system clipboard |
| `--version` | | Show version and exit |

## Configuration

Create `~/.config/tmux-shot/config.toml` for persistent preferences:

```toml
[general]
theme = "one-half-dark"
scale = 2
open = true               # always open after rendering

[font]
family = "DejaVuSansM Nerd Font Mono"  # path or font name
size = 16
line_height = 1.35

[layout]
padding = 20
tab_width = 8

[output]
directory = "/tmp"
clipboard = false
```

### Configuration Priority

Settings are resolved in this order (highest priority first):

1. **CLI arguments** -- `--font-size 14`
2. **Environment variables** -- `TMUX_SHOT_FONT_SIZE=14`
3. **Config file** -- `~/.config/tmux-shot/config.toml`
4. **Built-in defaults**

### Environment Variables

| Variable | Description |
|----------|-------------|
| `TMUX_SHOT_THEME` | Color theme name |
| `TMUX_SHOT_FONT` | Font file path |
| `TMUX_SHOT_FONT_SIZE` | Font size |
| `TMUX_SHOT_PADDING` | Padding |
| `TMUX_SHOT_SCALE` | Scale factor |
| `TMUX_SHOT_OUTPUT_DIR` | Output directory |

## Comparison with Similar Tools

| Feature | tmux-shot | [freeze](https://github.com/charmbracelet/freeze) | [silicon](https://github.com/Aloxaf/silicon) | [termshot](https://github.com/homeport/termshot) | [carbon](https://carbon.now.sh/) |
|---------|:---------:|:-----:|:-------:|:--------:|:------:|
| ANSI color parsing | Yes | Yes | No | Yes | No |
| Syntax highlighting | No | Yes | Yes | No | Yes |
| tmux integration | Native | Manual | No | No | No |
| Clipboard in + out | Yes | No | Partial | No | No |
| CJK support | Yes | Partial | Yes | Unknown | Yes |
| Config file | Yes | Yes | Yes | No | N/A |
| PNG output | Yes | Yes | Yes | Yes | Yes |
| SVG output | No | Yes | No | No | Yes |
| Offline | Yes | Yes | Yes | Yes | No |
| Install | pip | brew/go | cargo | brew/go | Web |

**tmux-shot** focuses on a niche the others don't cover well:

- **tmux-native**: purpose-built `copy-pipe` workflow -- select and press one key
- **ANSI + clipboard**: parses real terminal escape sequences AND supports clipboard I/O
- **CJK-first**: double-width character alignment is a first-class feature
- **Zero config**: works immediately with `pip install`, no Go/Rust toolchain needed

## Architecture

tmux-shot is structured as a modular Python package:

```
tmux_shot/
    cli.py        # CLI entry point and argument parsing
    config.py     # Config file, env vars, and defaults
    input.py      # Text acquisition (stdin / clipboard)
    ansi.py       # ANSI SGR escape sequence parser
    layout.py     # Character cell layout engine
    fonts.py      # Font loading with CJK fallback
    renderer.py   # Pillow-based image rendering
    themes.py     # Color scheme definitions
    output.py     # File save, clipboard copy, preview
```

See [docs/DESIGN.md](docs/DESIGN.md) for the full architecture and rendering pipeline documentation.

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Make your changes
4. Run linting and tests:
   ```bash
   ruff check .
   ruff format --check .
   pytest
   ```
5. Submit a pull request

### Development Setup

```bash
git clone https://github.com/<user>/tmux-shot.git
cd tmux-shot
pip install -e ".[toml]"
```

## License

[MIT](LICENSE)
