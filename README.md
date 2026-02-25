# tmux-shot

将 tmux 中选中的终端文本渲染为 PNG 截图，忠实还原终端字体和配色。

解决的问题：在 tmux 中与 AI 对话时，长内容需要截多张图拼接才能分享——tmux-shot 让你选中内容后一键生成完整长图。

## 特性

- **终端风格渲染**：使用等宽字体 + 终端配色，输出接近终端实际显示效果
- **CJK 支持**：中英文混排正确对齐，CJK 字符占双格子宽度
- **Retina 2x**：默认生成高清图片，macOS 预览自动按 Retina 缩放
- **暗色/亮色主题**：内置 One Half Dark / Light 配色，也可自定义
- **tmux 集成**：配合 copy-mode 按键绑定，选中即出图
- **灵活输入**：管道 stdin / 系统剪贴板自动检测

## 依赖

- Python 3.10+
- [Pillow](https://pillow.readthedocs.io/)
- macOS（使用 `pbpaste`、`osascript`、系统 CJK 字体）

## 安装

```bash
# 安装依赖
pip install Pillow

# 复制到 PATH
cp tmux-shot ~/.local/bin/
chmod +x ~/.local/bin/tmux-shot
```

## 用法

```bash
# 从剪贴板生成截图
tmux-shot --open

# 管道输入
pbpaste | tmux-shot --open

# 亮色主题
tmux-shot --light --open

# 自定义输出路径
tmux-shot -o /tmp/my-screenshot.png

# 同时复制图片到系统剪贴板
tmux-shot --clipboard
```

### tmux 集成

在 `~/.tmux.conf` 中添加：

```tmux
# Y = 复制到剪贴板 + 生成截图并打开
bind -T copy-mode-vi Y send-keys -X copy-pipe-and-cancel "pbcopy && pbpaste | tmux-shot --open"
```

重载配置后，在 copy-mode 中选中内容按 `Y` 即可。

## 参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `-o, --output` | `/tmp/tmux-shot-<时间戳>.png` | 输出路径 |
| `--font` | DejaVuSansM Nerd Font Mono | 字体文件路径 |
| `--font-size` | 16 | 字体大小（逻辑像素） |
| `--padding` | 20 | 内边距（逻辑像素） |
| `--line-height` | 1.35 | 行高倍数 |
| `--scale` | 2 | 渲染倍率（Retina 用 2） |
| `--bg` | `#282c34` | 背景色 |
| `--fg` | `#dcdfe4` | 前景色 |
| `--light` | - | 使用亮色主题 |
| `--open` | - | 生成后用预览打开 |
| `--clipboard` | - | 复制图片到系统剪贴板 |

## License

MIT
