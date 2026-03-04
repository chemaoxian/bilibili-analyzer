# bilibili-analyzer 测试指南

## 测试目录结构

```
tests/
├── __init__.py              # 测试包初始化
├── config.example.py        # 测试配置示例（可复制使用）
├── config.py                # 测试配置（需手动创建，已加入 .gitignore）
├── run_tests.py             # 测试运行器
├── test_analyzer.py         # BiliAnalyzer 模块测试
├── test_subtitle.py         # SubtitleProcessor 模块测试
├── test_clipper.py          # VideoClipper 模块测试
└── test_cli.py              # CLI 命令行接口测试
```

## 运行测试

### 快速运行

```bash
# 进入项目目录
cd tools/bilibili-analyzer

# 运行所有测试
python3 tests/run_tests.py
```

### 测试选项

```bash
# 显示详细输出
python3 tests/run_tests.py -v

# 仅运行单元测试（Mock 测试，不需要真实 API）
python3 tests/run_tests.py --unit

# 生成覆盖率报告
python3 tests/run_tests.py --coverage
```

### 使用 unittest 直接运行

```bash
# 运行单个测试文件
python3 -m unittest tests/test_analyzer.py

# 运行单个测试类
python3 -m unittest tests.test_analyzer.TestBiliAnalyzerInit

# 运行单个测试方法
python3 -m unittest tests.test_analyzer.TestBiliAnalyzerInit.test_init_with_bv_id
```

## 配置真实 API 测试

如需使用真实 B 站 API 进行测试：

1. 复制配置示例文件：
   ```bash
   cp tests/config.example.py tests/config.py
   ```

2. 编辑 `tests/config.py`，填入真实配置：
   ```python
   TEST_BV_ID = "BV1zZcYz1EMy"  # 替换为有效的 BV 号
   TEST_COOKIE_FILE = "./bilibili-cookie.txt"  # Cookie 文件路径（可选）
   TEST_OUTPUT_DIR = "./test_output"
   SKIP_COOKIE_TESTS = False  # 设置为 False 以启用 Cookie 测试
   ```

3. 运行测试：
   ```bash
   python3 tests/run_tests.py --live
   ```

## 测试覆盖

测试覆盖了以下模块：

### 1. analyzer.py - BiliAnalyzer 类

| 测试类 | 测试内容 |
|--------|----------|
| TestBiliAnalyzerInit | 初始化、参数验证 |
| TestBiliAnalyzerHeaders | 请求头生成、Cookie 处理 |
| TestMockVideoInfo | 视频信息获取（Mock） |
| TestMockDanmaku | 弹幕获取（Mock） |
| TestMockSubtitles | 字幕获取（Mock） |
| TestTimelineAnalysis | 时间轴分析、剪辑建议 |
| TestFormatTime | 时间格式化 |
| TestIntegration | 集成测试（需配置） |

### 2. subtitle.py - SubtitleProcessor 类

| 测试类 | 测试内容 |
|--------|----------|
| TestSubtitleProcessorInit | 初始化、文件加载 |
| TestFormatTimestamp | 时间戳格式化（SRT/VTT） |
| TestToSRT | SRT 转换 |
| TestToMarkdown | Markdown 转换 |
| TestExtractClip | 片段字幕提取 |
| TestSaveClip | 片段字幕保存 |
| TestMergeSRT | SRT 文件合并 |
| TestLoadFromFile | 文件加载 |

### 3. clipper.py - VideoClipper 类

| 测试类 | 测试内容 |
|--------|----------|
| TestVideoClipInit | VideoClip 数据类 |
| TestVideoClipperInit | 初始化、文件验证 |
| TestAddClip | 添加片段、链式调用 |
| TestFormatTime | 时间格式化 |
| TestCheckFFmpeg | ffmpeg 检查 |
| TestGenerateScript | Shell 脚本生成 |
| TestSplitClip | 单片段切分 |
| TestSplitAll | 批量切分 |
| TestFromTimeline | 从时间轴创建 |
| TestIntegration | 集成测试 |

### 4. cli.py - 命令行接口

| 测试类 | 测试内容 |
|--------|----------|
| TestCLIHelp | 帮助信息 |
| TestAnalyzeCommand | analyze 命令 |
| TestDownloadCommand | download 命令 |
| TestDanmakuCommand | danmaku 命令 |
| TestSubtitleCommand | subtitle 命令 |
| TestClipCommand | clip 命令 |
| TestScriptCommand | script 命令 |
| TestErrorHandling | 错误处理 |

## 测试统计

- **总测试数**: 87
- **单元测试**: 86（Mock 测试）
- **集成测试**: 1（需配置 BV 号和 Cookie）

## 常见问题

### Q: 为什么有些测试被跳过？
A: 集成测试需要配置真实的 BV 号。如果 `tests/config.py` 中 `TEST_BV_ID` 为空，集成测试会被自动跳过。

### Q: 如何查看测试覆盖率？
A: 使用 `--coverage` 选项运行测试：
```bash
python3 tests/run_tests.py --coverage
```
会生成 HTML 报告到 `tests/htmlcov/` 目录。

### Q: 测试失败怎么办？
A: 检查错误信息。大部分测试使用 Mock，不应该失败。如果失败，可能是：
- Mock 配置问题
- 代码逻辑变更
- 环境问题

### Q: 如何添加新测试？
A: 遵循现有测试结构：
1. 在对应模块的测试文件中添加测试类或方法
2. 使用 `unittest.TestCase` 基类
3. 测试方法以 `test_` 开头
4. 使用装饰器如 `@patch` 进行 Mock

## 贡献指南

提交代码前，请确保：
1. 所有测试通过
2. 新增功能有对应测试
3. 测试覆盖率没有显著下降
