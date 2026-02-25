# tmux-shot

将终端文本渲染为 PNG 截图，完整保留 ANSI 颜色。专为需要分享长篇终端输出的 tmux 用户打造。

> English version: [README.md](README.md)

## 功能特性

- **ANSI 颜色渲染** -- 忠实还原 8/16/256/真彩色 ANSI 转义序列，支持粗体、暗淡、斜体、下划线、删除线、反色
- **CJK 支持** -- 中日韩双宽字符正确对齐，自动回退 CJK 字体
- **符号回退** -- 主字体缺失的 Unicode 符号（如 `U+23FA`）自动通过位图哈希检测并回退到备用字体
- **Retina / HiDPI** -- 默认 2x 渲染，macOS 预览以正确的逻辑尺寸显示
- **主题** -- 内置 One Half Dark 和 One Half Light 配色方案，支持 `--bg`/`--fg` 自定义覆盖
- **tmux 集成** -- copy-mode 中一键截图，通过 `capture-pane -e` 保留 ANSI 颜色
- **灵活输入** -- 自动读取 stdin 管道或系统剪贴板
- **剪贴板输出** -- 渲染后的 PNG 直接复制到系统剪贴板
- **配置文件** -- 通过 `~/.config/tmux-shot/config.toml` 持久化偏好设置
- **跨平台** -- 主要支持 macOS，同时支持 Linux

## 安装

**依赖：Python 3.10+ 和 [Pillow](https://pillow.readthedocs.io/)**

```bash
# 从 PyPI 安装
pip install tmux-shot

# 使用 pipx（隔离环境）
pipx install tmux-shot

# 从源码安装
git clone https://github.com/Async23/tmux-shot.git
cd tmux-shot
pip install -e .
```

## 快速开始

```bash
# 从剪贴板截图，在预览中打开
tmux-shot --open

# 管道任意命令输出
ls --color=always | tmux-shot --open

# 亮色主题 + 复制到剪贴板
echo "hello world" | tmux-shot --light --clipboard
```

## tmux 集成

tmux-shot 使用 `tmux capture-pane -e` 保留 ANSI 转义序列。集成需要一个辅助脚本 `tmux-shot-capture`，将 copy-mode 的选区坐标转换为 capture-pane 的行范围。

### 配置步骤

1. 将辅助脚本安装到 `$PATH`：

```bash
# 从项目中复制
cp scripts/tmux-shot-capture ~/.local/bin/
chmod +x ~/.local/bin/tmux-shot-capture
```

2. 添加到 `~/.tmux.conf`：

```tmux
# y = 复制到剪贴板（默认行为）
bind -T copy-mode-vi y send-keys -X copy-pipe-and-cancel "pbcopy"

# Y = 截图选区（保留 ANSI 颜色）+ 复制到剪贴板
bind -T copy-mode-vi Y if-shell -F '#{selection_present}' \
  'run-shell -b "tmux-shot-capture #{selection_start_y} #{selection_end_y} #{history_size} --open --clipboard" ; \
   send-keys -X copy-pipe-and-cancel "pbcopy"' \
  'display-message "No selection"'
```

3. 重载 tmux 配置：`tmux source ~/.tmux.conf`

### 使用方法

1. 进入 copy-mode：`prefix + [`（或你自定义的按键）
2. 用 `v` 和方向键选择文本
3. 按 `Y` -- 生成 PNG 截图，复制到剪贴板，并在预览中打开

### 工作原理

```
在 copy-mode 中按下 Y
  --> tmux 展开 #{selection_start_y}、#{selection_end_y}、#{history_size}
  --> tmux-shot-capture 转换为 capture-pane 行范围
  --> tmux capture-pane -e -p -S <start> -E <end>（保留 ANSI）
  --> 管道传输给 tmux-shot 渲染
  --> PNG 保存、复制到剪贴板、在预览中打开
```

> **为什么不直接用 `copy-pipe`？** `copy-pipe` 只发送纯文本，会去除所有 ANSI 转义序列。通过 `capture-pane -e`，我们保留了颜色、粗体、斜体等所有终端格式。

> **为什么 `run-shell -b` 要放在 `copy-pipe-and-cancel` 之前？** tmux 的格式变量（如 `#{selection_start_y}`）在处理 `;` 链中的每个命令时展开。如果 `copy-pipe-and-cancel` 先执行，会清除选区 -- 导致后续命令的格式变量为空。将 `run-shell -b` 放在前面，确保在选区存在时捕获变量值。

### 直接捕获窗格

```bash
# 捕获可见窗格内容
tmux capture-pane -p -e | tmux-shot --open

# 捕获含滚动历史（最近 500 行）
tmux capture-pane -p -e -S -500 | tmux-shot --open
```

> **提示：** 使用 `tmux capture-pane` 时务必加 `-e` 参数以保留 ANSI 转义序列。

## CLI 参考

| 选项 | 默认值 | 说明 |
|------|--------|------|
| `-o, --output PATH` | `/tmp/tmux-shot-<时间戳>.png` | 输出文件路径 |
| `--theme NAME` | `one-half-dark` | 配色主题（`one-half-dark`、`one-half-light`） |
| `--light` | | `--theme one-half-light` 的快捷方式 |
| `--font PATH` | 自动检测 | 等宽字体 `.ttf`/`.otf` 文件路径 |
| `--font-size N` | `16` | 字号（逻辑像素） |
| `--padding N` | `20` | 图片内边距（逻辑像素） |
| `--line-height F` | `1.0` | 行高倍数 |
| `--scale N` | `2` | HiDPI 缩放因子（2 = Retina） |
| `--bg COLOR` | 主题默认 | 覆盖背景色（`#rrggbb`） |
| `--fg COLOR` | 主题默认 | 覆盖前景色（`#rrggbb`） |
| `--open` | `false` | 渲染后自动打开图片 |
| `--clipboard` | `false` | 复制图片到系统剪贴板 |
| `--version` | | 显示版本号 |

## 配置

创建 `~/.config/tmux-shot/config.toml` 持久化偏好设置：

```toml
[general]
theme = "one-half-dark"
scale = 2
open = true               # 渲染后始终打开

[font]
family = "DejaVuSansM Nerd Font Mono"  # 字体路径或名称
size = 16
line_height = 1.0

[layout]
padding = 20
tab_width = 8

[output]
directory = "/tmp"
clipboard = false
```

### 配置优先级

设置按以下顺序解析（优先级从高到低）：

1. **CLI 参数** -- `--font-size 14`
2. **环境变量** -- `TMUX_SHOT_FONT_SIZE=14`
3. **配置文件** -- `~/.config/tmux-shot/config.toml`
4. **内置默认值**

### 环境变量

| 变量 | 说明 |
|------|------|
| `TMUX_SHOT_THEME` | 配色主题名称 |
| `TMUX_SHOT_FONT` | 字体文件路径 |
| `TMUX_SHOT_FONT_SIZE` | 字号 |
| `TMUX_SHOT_PADDING` | 内边距 |
| `TMUX_SHOT_SCALE` | 缩放因子 |
| `TMUX_SHOT_OUTPUT_DIR` | 输出目录 |

## 与同类工具的对比

| 特性 | tmux-shot | [freeze](https://github.com/charmbracelet/freeze) | [silicon](https://github.com/Aloxaf/silicon) | [termshot](https://github.com/homeport/termshot) | [carbon](https://carbon.now.sh/) |
|------|:---------:|:-----:|:-------:|:--------:|:------:|
| ANSI 颜色解析 | Yes | Yes | No | Yes | No |
| 语法高亮 | No | Yes | Yes | No | Yes |
| tmux 集成 | 原生 | 手动 | No | No | No |
| 剪贴板输入+输出 | Yes | No | 部分 | No | No |
| CJK 支持 | Yes | 部分 | Yes | 未知 | Yes |
| 符号回退 | Yes | No | No | No | No |
| 配置文件 | Yes | Yes | Yes | No | N/A |
| PNG 输出 | Yes | Yes | Yes | Yes | Yes |
| SVG 输出 | No | Yes | No | No | Yes |
| 离线使用 | Yes | Yes | Yes | Yes | No |
| 安装方式 | pip | brew/go | cargo | brew/go | Web |

**tmux-shot** 专注于其他工具覆盖不好的场景：

- **tmux 原生**：基于 `capture-pane` 的一键截图工作流
- **ANSI + 剪贴板**：解析真实终端转义序列，同时支持剪贴板输入输出
- **CJK 优先**：双宽字符对齐是一等公民特性
- **符号感知**：位图哈希 tofu 检测 + 自动回退字体
- **零配置**：`pip install` 即可使用，无需 Go/Rust 工具链

## 架构

tmux-shot 采用模块化 Python 包结构：

```
tmux_shot/
    cli.py        # CLI 入口与参数解析
    config.py     # 配置文件、环境变量、默认值
    input.py      # 文本获取（stdin / 剪贴板）
    ansi.py       # ANSI SGR 转义序列解析器
    layout.py     # 字符单元格布局引擎
    fonts.py      # 字体加载，CJK + 符号回退
    renderer.py   # 基于 Pillow 的图像渲染
    themes.py     # 配色方案定义
    output.py     # 文件保存、剪贴板复制、预览
```

**渲染管道：**

```
原始文本 (stdin/剪贴板)
  --> ANSI 解析器 (ansi.py)     --> StyledSpan[]
  --> 布局引擎 (layout.py)      --> LayoutLine[Cell[]]
  --> 渲染器 (renderer.py)       --> PIL Image
  --> 输出 (output.py)           --> PNG 文件 / 剪贴板 / 预览
```

**字体回退链：**

```
字符渲染
  --> ASCII (< 0x80)?           --> 主字体（含粗体/斜体变体）
  --> CJK 双宽字符?             --> CJK 回退字体（Hiragino Sans GB 等）
  --> 主字体有字形?              --> 主字体
  --> 符号回退字体（tofu 检测）   --> STIXTwoMath / Apple Symbols
```

详细架构文档请参阅 [docs/DESIGN.md](docs/DESIGN.md)。

## 贡献

欢迎贡献！请：

1. Fork 仓库
2. 创建功能分支（`git checkout -b feature/my-feature`）
3. 提交你的修改
4. 运行代码检查和测试：
   ```bash
   ruff check .
   ruff format --check .
   pytest
   ```
5. 提交 Pull Request

### 开发环境

```bash
git clone https://github.com/Async23/tmux-shot.git
cd tmux-shot
pip install -e ".[toml]"
```

## 许可证

[MIT](LICENSE)
