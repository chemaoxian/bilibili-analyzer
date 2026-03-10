# bilibili-analyzer

B 站视频分析工具 - 一键获取视频详细信息、弹幕、字幕，生成时间轴分析报告。

## 功能特性

- 📺 **视频分析** - 获取视频详细信息、统计数据
- 💬 **弹幕提取** - 下载视频弹幕，支持 JSON 格式
- 📝 **字幕提取** - 下载 CC 字幕，支持转换为 SRT 格式
- 🎬 **剪辑建议** - 基于弹幕热点自动生成剪辑建议
- 📊 **时间轴报告** - 生成详细的时间轴分析报告
- ✂️ **视频切分** - 根据时间点切分视频片段
- 📥 **视频下载** - 下载视频（支持高质量，需要 Cookie）

## 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 基本用法

```bash
# 分析视频，生成报告
python cli.py analyze BV1zZcYz1EMy

# 下载视频
python cli.py download BV1zZcYz1EMy -o output.mp4

# 提取弹幕
python cli.py danmaku BV1zZcYz1EMy

# 提取字幕
python cli.py subtitle BV1zZcYz1EMy

# 切分视频片段
python cli.py clip video.mp4

# 生成切分脚本
python cli.py script video.mp4
```

## 命令详解

### analyze - 分析视频

分析视频并生成完整的报告，包括：
- 视频基本信息（标题、UP 主、时长等）
- 统计数据（播放、点赞、弹幕数等）
- 弹幕和字幕数据
- 剪辑建议
- 时间轴报告

```bash
python cli.py analyze BV1zZcYz1EMy
python cli.py analyze BV1zZcYz1EMy -o ./output
python cli.py analyze BV1zZcYz1EMy -c ./bilibili-cookie.txt
```

输出文件：
- `{BV 号}_full.json` - 完整数据
- `{BV 号}_danmaku.json` - 弹幕数据
- `{BV 号}_subtitles.json` - 字幕数据
- `{BV 号}_timeline.md` - 时间轴报告

### download - 下载视频

下载 B 站视频到本地。

```bash
python cli.py download BV1zZcYz1EMy
python cli.py download BV1zZcYz1EMy -o my_video.mp4
```

**提示**：如需下载高质量视频，请创建 Cookie 文件：
1. 登录 B 站
2. 复制 Cookie
3. 保存到 `bilibili-cookie.txt` 文件
4. 使用 `-c` 参数指定 Cookie 文件路径

### danmaku - 提取弹幕

提取视频弹幕并保存为 JSON 文件。

```bash
python cli.py danmaku BV1zZcYz1EMy
python cli.py danmaku BV1zZcYz1EMy -o danmaku.json
```

### subtitle - 提取字幕

提取视频 CC 字幕并转换为 SRT 格式。

```bash
python cli.py subtitle BV1zZcYz1EMy
python cli.py subtitle BV1zZcYz1EMy -o ./subtitles
```

### clip - 切分视频

根据预设时间点切分视频片段。

```bash
python cli.py clip input.mp4
python cli.py clip input.mp4 -o clips
```

### script - 生成切分脚本

生成 Shell 脚本用于后续切分视频。

```bash
python cli.py script input.mp4
python cli.py script input.mp4 -s cut.sh
```

## 编程接口

### 使用 Analyzer

```python
from src.analyzer import BiliAnalyzer

# 创建分析器
analyzer = BiliAnalyzer(bv_id="BV1zZcYz1EMy")

# 获取视频信息
info = analyzer.get_video_info()
print(f"标题：{info['title']}")
print(f"UP 主：{info['owner']['name']}")

# 获取统计数据
stats = analyzer.get_video_stats()
print(f"播放量：{stats['view']}")
print(f"点赞数：{stats['like']}")

# 获取弹幕
danmaku = analyzer.get_danmaku()
print(f"弹幕数：{len(danmaku)}")

# 获取字幕
subtitles = analyzer.get_subtitles()
for sub in subtitles:
    print(f"{sub['language']}: {len(sub['content'])} 条")

# 完整分析
analyzer.analyze(output_dir="./output")
```

### 使用 SubtitleProcessor

```python
from src.subtitle import SubtitleProcessor

# 加载字幕文件
processor = SubtitleProcessor("BV1zZcYz1EMy_subtitle.json")

# 转换为 SRT
processor.to_srt("output.srt")

# 转换为 Markdown
processor.to_markdown("output.md", title="视频字幕")

# 提取片段字幕
subs = processor.extract_clip(start_sec=60, end_sec=90)

# 保存片段字幕
processor.save_clip(
    start_sec=60,
    end_sec=90,
    output_dir="./clips",
    name="highlight"
)
```

### 使用 VideoClipper

```python
from src.clipper import VideoClipper

# 创建切分器
clipper = VideoClipper("input.mp4", output_dir="clips")

# 添加片段（支持链式调用）
clipper.add_clip("intro", start=0, duration=30, description="开场") \
       .add_clip("highlight", start=60, duration=30, description="亮点")

# 开始切分
clipper.split_all()

# 或生成脚本
clipper.generate_script("cut.sh")
```

## 输出格式说明

### JSON 数据格式

```json
{
  "info": {
    "title": "视频标题",
    "bvid": "BV1zZcYz1EMy",
    "duration": 600,
    "owner": {"name": "UP 主名称"},
    ...
  },
  "stats": {
    "view": 100000,
    "danmaku": 5000,
    "like": 8000,
    ...
  },
  "danmaku": [...],
  "subtitles": [...],
  "clips": [...]
}
```

### 时间轴报告

Markdown 格式的时间轴报告包含：
- 视频基本信息
- 统计数据表格
- 推荐剪辑片段
- 弹幕热点时间轴
- 完整字幕时间轴
- PPT 使用建议

## 常见问题

### Q: 下载视频失败？
A: 高质量视频下载需要登录 Cookie。请按照以下步骤操作：
1. 浏览器登录 B 站
2. 打开开发者工具（F12）
3. 找到任意请求的 Cookie
4. 复制到 `bilibili-cookie.txt` 文件

### Q: 没有 CC 字幕怎么办？
A: 不是所有视频都有 CC 字幕。对于没有字幕的视频，可以使用 Whisper 等工具进行语音识别。

### Q: 切分视频失败？
A: 视频切分需要安装 ffmpeg。请确保已安装：
```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg
```

## 项目结构

```
bilibili-analyzer/
├── cli.py                 # 命令行入口
├── requirements.txt       # Python 依赖
├── src/
│   ├── __init__.py        # 包初始化
│   ├── analyzer.py        # 核心分析模块
│   ├── subtitle.py        # 字幕处理模块
│   └── clipper.py         # 视频切分模块
├── examples/
│   └── example_usage.py   # 使用示例
├── tests/
│   ├── __init__.py
│   ├── config.example.py  # 测试配置示例
│   ├── run_tests.py       # 测试运行器
│   ├── test_analyzer.py   # BiliAnalyzer 测试
│   ├── test_subtitle.py   # SubtitleProcessor 测试
│   ├── test_clipper.py    # VideoClipper 测试
│   └── test_cli.py        # CLI 测试
└── tests/README.md        # 测试文档
```

## 测试

运行所有测试：

```bash
python3 tests/run_tests.py
```

运行单个测试文件：

```bash
python3 -m unittest tests/test_analyzer.py
```

生成覆盖率报告：

```bash
python3 tests/run_tests.py --coverage
```

详细测试文档请查看 [tests/README.md](tests/README.md)。

## 开发计划

- [ ] 支持多 P 视频
- [ ] 支持批量处理
- [ ] 添加 GUI 界面
- [ ] 支持更多输出格式

## 许可证

MIT License

## ⚠️ 免责声明

**本工具仅供学习和个人研究使用**，使用前请仔细阅读以下声明：

### 合规使用
- 请使用**自己的** B 站账号 Cookie
- **请勿将 Cookie 分享给他人**
- 请勿用于批量下载或商业用途
- 弹幕和字幕版权归 B 站及 UP 主所有
- 使用本工具即表示您同意遵守 [B 站用户协议](https://www.bilibili.com/protocol/user) 和相关法律法规

### Cookie 安全说明

⚠️ **重要**：Cookie 包含账号敏感信息，请妥善保管：
- 仅存储在本地安全位置
- 不要上传到代码仓库（已添加到 `.gitignore`）
- 不要分享给任何人
- 定期更新 Cookie

**本工具不会存储或传输您的 Cookie，所有处理都在本地完成。**

### API 使用限制

B 站 API 有访问频率限制，建议：
- 单个 IP 不要频繁请求（建议间隔 >1 秒）
- 大量请求可能触发 B 站风控

## 贡献

欢迎提交 Issue 和 Pull Request！
