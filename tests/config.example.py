#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试配置文件示例

使用说明:
1. 复制此文件为 config.py
2. 填入真实的 BV 号和 Cookie 文件路径
3. 运行测试

注意：config.py 文件已被添加到 .gitignore，不会泄露敏感信息
"""

# 测试用的 B 站视频 BV 号
# 请替换为你想要测试的视频 BV 号
TEST_BV_ID = "BV1xxxxxxxxx"

# Cookie 文件路径（可选，用于下载高质量视频）
# 如无需下载视频测试，可留空
TEST_COOKIE_FILE = ""  # 例如："./bilibili-cookie.txt"

# 测试输出目录
TEST_OUTPUT_DIR = "./test_output"

# 是否跳过需要 Cookie 的测试
SKIP_COOKIE_TESTS = True
