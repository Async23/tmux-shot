# tmux-shot Requirements

## Project Vision

**tmux-shot** is a CLI tool that renders terminal text (with ANSI colors) into PNG screenshots, faithfully reproducing the look of your terminal. It is purpose-built for tmux users who need to share long terminal output as a single image.

### Problem Statement

When working in tmux (especially with AI assistants), conversations and command output often span many screens. Sharing this content requires either:
- Taking multiple OS screenshots and stitching them together
- Copy-pasting plain text and losing all formatting and colors
- Using web-based tools that don't understand terminal ANSI output

tmux-shot solves this with a single command: select text in tmux copy-mode, press a key, get a pixel-perfect PNG.

## Target Users

1. **Developers using tmux daily** — who share terminal output in chats, docs, or social media
2. **AI/LLM power users** — who have long conversations in terminal-based AI tools and need to share them
3. **Technical writers & bloggers** — who want terminal screenshots for documentation without browser tools
4. **DevOps/SRE engineers** — who need to capture command output for incident reports or runbooks

## Core Use Cases (User Stories)

### US-1: One-key screenshot from tmux
> As a tmux user, I want to select text in copy-mode and press a single key to generate a PNG screenshot, so I can share terminal content without leaving the terminal.

### US-2: ANSI color preservation
> As a developer, I want the screenshot to faithfully render ANSI colors (syntax highlighting, colored diffs, `ls --color` output), so the image looks like my actual terminal.

### US-3: Long content as a single image
> As an AI chat user, I want to capture an entire long conversation (100+ lines) as one tall image, so I don't need to stitch multiple screenshots together.

### US-4: Quick share to clipboard
> As a user, I want to copy the generated image directly to my system clipboard, so I can paste it into Slack/Discord/WeChat immediately.

### US-5: CJK text support
> As a Chinese/Japanese/Korean user, I want CJK characters to render correctly with proper double-width alignment, so mixed-language terminal output looks right.

### US-6: Customizable appearance
> As a user, I want to choose themes, fonts, padding, and other visual options, so the screenshot matches my personal preference or brand.

### US-7: Pipe-friendly CLI
> As a power user, I want to pipe any command's output into tmux-shot (`cmd | tmux-shot`), so I can screenshot output from any source, not just tmux.

## Functional Requirements

### P0 — MVP (Must Have)

| ID | Feature | Description |
|----|---------|-------------|
| F-01 | **Stdin / clipboard input** | Read text from stdin pipe or system clipboard (macOS `pbpaste`) |
| F-02 | **ANSI color rendering** | Parse SGR escape sequences: reset, bold, dim, italic, underline, standard 8/16 colors, 256-color, 24-bit truecolor for both foreground and background |
| F-03 | **PNG output** | Render to PNG with configurable DPI/scale (default 2x for Retina) |
| F-04 | **CJK support** | Correct double-width character rendering with font fallback |
| F-05 | **Built-in themes** | At least dark and light themes with sensible defaults (One Half Dark/Light) |
| F-06 | **tmux integration** | Document and support `copy-pipe` binding for one-key workflow |
| F-07 | **CLI arguments** | `--output`, `--theme`, `--font`, `--font-size`, `--padding`, `--scale`, `--open`, `--clipboard` |
| F-08 | **Clipboard output** | Copy resulting PNG to system clipboard (macOS `osascript`) |
| F-09 | **Auto-open preview** | Option to open the generated image with the default viewer |

### P1 — Important (Should Have)

| ID | Feature | Description |
|----|---------|-------------|
| F-10 | **Config file** | Support `~/.config/tmux-shot/config.toml` for persistent preferences |
| F-11 | **Custom themes** | User-defined color schemes (16-color palette + bg/fg) via config or CLI |
| F-12 | **Window chrome** | Optional macOS-style title bar with traffic light buttons |
| F-13 | **Line numbers** | Optional line number gutter |
| F-14 | **SVG output** | Support SVG as an alternative output format |
| F-15 | **Shadow / rounded corners** | Optional drop shadow and corner radius for a polished look |
| F-16 | **Watermark / title** | Optional title text or watermark on the image |
| F-17 | **tmux pane capture** | `tmux capture-pane` integration to grab the current pane content directly |

### P2 — Nice to Have (Could Have)

| ID | Feature | Description |
|----|---------|-------------|
| F-18 | **Nerd Font icon rendering** | Render Nerd Font / Powerline glyphs correctly |
| F-19 | **WebP output** | Support WebP as output format |
| F-20 | **Interactive mode** | TUI for adjusting theme/padding and previewing the result |
| F-21 | **Linux / Wayland clipboard** | Support `xclip`, `xsel`, `wl-copy` for Linux |
| F-22 | **URL shortening** | Upload image and return a shareable URL |
| F-23 | **Strip ANSI option** | Option to strip ANSI codes and render plain text |
| F-24 | **Max width wrapping** | Wrap long lines at a configurable column width |

## Non-Functional Requirements

### Performance

| Requirement | Target |
|-------------|--------|
| Render time (100 lines, ASCII) | < 500ms |
| Render time (500 lines, mixed CJK) | < 2s |
| Memory usage | < 200MB for typical screenshots |
| Startup time | < 300ms (Python cold start acceptable) |

### Compatibility

| Requirement | Details |
|-------------|---------|
| Python | 3.10+ |
| OS (primary) | macOS 13+ (Ventura and later) |
| OS (secondary) | Linux (Ubuntu 22.04+, Fedora 38+) |
| Terminal | Any terminal that outputs ANSI — optimized for Ghostty + tmux |
| Fonts | TrueType (.ttf), OpenType (.otf), TrueType Collection (.ttc) |

### Installability

| Method | Priority |
|--------|----------|
| `pip install tmux-shot` | P0 |
| `pipx install tmux-shot` | P0 |
| `brew install tmux-shot` | P1 |
| Single-file script (current) | Maintained as fallback |

### Quality

- Unit tests for ANSI parser and layout engine
- Integration tests comparing rendered output against reference images
- CI with GitHub Actions (lint + test on macOS and Linux)

## Competitive Landscape

### Tool Comparison Matrix

| Feature | **tmux-shot** | [freeze](https://github.com/charmbracelet/freeze) | [silicon](https://github.com/Aloxaf/silicon) | [termshot](https://github.com/homeport/termshot) | [termframe](https://github.com/pamburus/termframe) | [carbon](https://carbon.now.sh/) |
|---------|:---:|:---:|:---:|:---:|:---:|:---:|
| **Language** | Python | Go | Rust | Go | Rust | JS (web) |
| **Offline** | Yes | Yes | Yes | Yes | Yes | No |
| **ANSI color parsing** | P0 | Yes | No | Yes | Yes | No |
| **Syntax highlighting** | No | Yes | Yes | No | No | Yes |
| **PNG output** | Yes | Yes | Yes | Yes | No | Yes |
| **SVG output** | P1 | Yes | No | No | Yes | Yes |
| **tmux integration** | Native | Manual | No | No | No | No |
| **Clipboard in/out** | Yes | No | Yes | No | No | No |
| **CJK support** | Yes | Partial | Yes | Unknown | Unknown | Yes |
| **Window chrome** | P1 | Yes | Yes | Yes | Yes | Yes |
| **Custom themes** | P1 | Yes | Yes | No | Yes | Yes |
| **Config file** | P1 | Yes | Yes | No | Yes | N/A |
| **Interactive TUI** | P2 | Yes | No | No | No | Yes (web) |
| **Retina/HiDPI** | Yes | Yes | Yes | No | N/A (SVG) | Yes |
| **Install method** | pip | brew/go | cargo | brew/go | cargo | Web |
| **Runs a command** | No | Yes | No | Yes | Yes | No |

### Tool Profiles

**[charmbracelet/freeze](https://github.com/charmbracelet/freeze)** — The most feature-rich CLI option. Supports both code (syntax highlighting) and terminal output (ANSI). Has an interactive TUI, config files, SVG/PNG/WebP output, window chrome, shadows. Written in Go. *Weakness*: no native tmux integration, no clipboard I/O, heavier binary.

**[Aloxaf/silicon](https://github.com/Aloxaf/silicon)** — Fast Rust tool focused on source code screenshots with syntax highlighting (uses syntect). Does NOT parse ANSI escape codes — it's a code screenshotter, not a terminal output screenshotter. *Weakness*: no ANSI support, no terminal output rendering.

**[homeport/termshot](https://github.com/homeport/termshot)** — Runs a command in a pseudo-terminal and captures ANSI output as PNG. High-fidelity ANSI rendering. *Weakness*: must execute the command (can't take piped text), limited customization, no clipboard, no config file.

**[pamburus/termframe](https://github.com/pamburus/termframe)** — Rust tool that runs a command and exports SVG with full ANSI style support (bold, italic, 256-color, truecolor). Excellent theme collection. *Weakness*: SVG-only output, must execute a command, no clipboard.

**[carbon-app/carbon](https://github.com/carbon-app/carbon)** — Beautiful web-based code screenshot tool. Requires a browser and internet. Has a CLI wrapper (`carbon-now-cli`) but it's slow. *Weakness*: online-only, no ANSI support, high latency, no terminal integration.

## Differentiation

tmux-shot differentiates from the competition in three key ways:

1. **tmux-native workflow**: Purpose-built for the `copy-pipe` binding pattern. Select text in tmux copy-mode → press one key → get a PNG. No other tool offers this level of tmux integration out of the box.

2. **ANSI colors + clipboard I/O**: The combination of parsing ANSI escape sequences (like termshot/termframe) AND supporting clipboard input/output (like silicon) is unique. Most tools do one or the other.

3. **CJK-first design**: Proper double-width character alignment with font fallback is a first-class feature, not an afterthought. This matters for the large user base working in CJK languages.

4. **Zero-config sensible defaults**: Works immediately with `pip install` — no Go/Rust toolchain needed, no config files required. Defaults match common terminal setups (dark theme, Retina, Nerd Font).
