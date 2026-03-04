#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CLI 命令行接口测试

测试范围:
1. 命令行参数解析
2. 各子命令的基本功能
3. 错误处理
"""

import unittest
import sys
import os
import tempfile
import shutil
from io import StringIO
from unittest.mock import patch, MagicMock

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


class TestCLIHelp(unittest.TestCase):
    """测试帮助信息"""

    def test_main_help(self):
        """测试主帮助信息"""
        from cli import main

        # 捕获帮助输出
        with patch('sys.argv', ['cli.py', '--help']):
            with patch('sys.stdout', new=StringIO()) as fake_out:
                try:
                    main()
                except SystemExit:
                    pass  # argparse 会退出

                output = fake_out.getvalue()

        # 验证帮助信息包含所有子命令
        self.assertIn("analyze", output)
        self.assertIn("download", output)
        self.assertIn("danmaku", output)
        self.assertIn("subtitle", output)
        self.assertIn("clip", output)
        self.assertIn("script", output)


class TestAnalyzeCommand(unittest.TestCase):
    """测试 analyze 命令"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    @patch('cli.BiliAnalyzer')
    def test_analyze_basic(self, mock_analyzer_class):
        """测试基本分析命令"""
        from cli import main

        # 设置 mock
        mock_analyzer = MagicMock()
        mock_analyzer.analyze.return_value = {
            "info": {"title": "测试视频"},
            "stats": {"view": 1000}
        }
        mock_analyzer_class.return_value = mock_analyzer

        with patch('sys.argv', ['cli.py', 'analyze', 'BV1234567890', '-o', self.temp_dir]):
            try:
                main()
            except SystemExit:
                pass

        # 验证调用
        mock_analyzer_class.assert_called_once()
        mock_analyzer.analyze.assert_called_once()

    @patch('cli.BiliAnalyzer')
    def test_analyze_with_cookie(self, mock_analyzer_class):
        """测试带 Cookie 的分析命令"""
        from cli import main

        cookie_file = os.path.join(self.temp_dir, "cookie.txt")
        with open(cookie_file, "w") as f:
            f.write("test=cookie")

        mock_analyzer = MagicMock()
        mock_analyzer_class.return_value = mock_analyzer

        with patch('sys.argv', ['cli.py', 'analyze', 'BV1234567890', '-c', cookie_file]):
            try:
                main()
            except SystemExit:
                pass

        # 验证 cookie 文件被传递
        args, kwargs = mock_analyzer_class.call_args
        self.assertEqual(kwargs.get('cookie_file'), cookie_file)


class TestDownloadCommand(unittest.TestCase):
    """测试 download 命令"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    @patch('cli.BiliAnalyzer')
    def test_download_basic(self, mock_analyzer_class):
        """测试基本下载命令"""
        from cli import main

        mock_analyzer = MagicMock()
        mock_analyzer.download_video.return_value = True
        mock_analyzer_class.return_value = mock_analyzer

        output_path = os.path.join(self.temp_dir, "output.mp4")

        with patch('sys.argv', ['cli.py', 'download', 'BV1234567890', '-o', output_path]):
            try:
                main()
            except SystemExit:
                pass

        mock_analyzer.download_video.assert_called_once()


class TestDanmakuCommand(unittest.TestCase):
    """测试 danmaku 命令"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    @patch('cli.BiliAnalyzer')
    @patch('builtins.open')
    def test_danmaku_basic(self, mock_file, mock_analyzer_class):
        """测试基本弹幕提取命令"""
        from cli import main

        mock_analyzer = MagicMock()
        mock_analyzer.get_danmaku.return_value = [
            {"time": 10.0, "text": "测试弹幕"}
        ]
        mock_analyzer_class.return_value = mock_analyzer

        output_path = os.path.join(self.temp_dir, "danmaku.json")

        with patch('sys.argv', ['cli.py', 'danmaku', 'BV1234567890', '-o', output_path]):
            try:
                main()
            except SystemExit:
                pass

        mock_analyzer.get_danmaku.assert_called_once()


class TestSubtitleCommand(unittest.TestCase):
    """测试 subtitle 命令"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    @patch('cli.BiliAnalyzer')
    def test_subtitle_basic(self, mock_analyzer_class):
        """测试基本字幕提取命令"""
        from cli import main

        mock_analyzer = MagicMock()
        mock_analyzer.get_subtitles.return_value = [
            {"language": "zh-CN", "content": []}
        ]
        mock_analyzer_class.return_value = mock_analyzer

        with patch('sys.argv', ['cli.py', 'subtitle', 'BV1234567890', '-o', self.temp_dir]):
            try:
                main()
            except SystemExit:
                pass

        mock_analyzer.get_subtitles.assert_called_once()


class TestClipCommand(unittest.TestCase):
    """测试 clip 命令"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.test_video = os.path.join(self.temp_dir, "test.mp4")
        with open(self.test_video, "w") as f:
            f.write("")

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    @patch('cli.VideoClipper')
    def test_clip_basic(self, mock_clipper_class):
        """测试基本切分命令"""
        from cli import main

        mock_clipper = MagicMock()
        mock_clipper.split_all.return_value = ["clip1.mp4"]
        mock_clipper_class.return_value = mock_clipper

        with patch('sys.argv', ['cli.py', 'clip', self.test_video, '-o', self.temp_dir]):
            try:
                main()
            except SystemExit:
                pass

        mock_clipper_class.assert_called_once()
        mock_clipper.split_all.assert_called_once()


class TestScriptCommand(unittest.TestCase):
    """测试 script 命令"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.test_video = os.path.join(self.temp_dir, "test.mp4")
        with open(self.test_video, "w") as f:
            f.write("")

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    @patch('cli.VideoClipper')
    def test_script_basic(self, mock_clipper_class):
        """测试基本脚本生成命令"""
        from cli import main

        mock_clipper = MagicMock()
        mock_clipper_class.return_value = mock_clipper

        script_path = os.path.join(self.temp_dir, "cut.sh")

        with patch('sys.argv', ['cli.py', 'script', self.test_video, '-s', script_path]):
            try:
                main()
            except SystemExit:
                pass

        mock_clipper.generate_script.assert_called_once()


class TestErrorHandling(unittest.TestCase):
    """测试错误处理"""

    def test_invalid_bv_id(self):
        """测试无效 BV 号处理"""
        from cli import main

        # 空 BV 号应该报错
        with patch('sys.argv', ['cli.py', 'analyze', '']):
            with self.assertRaises(SystemExit):
                main()

    def test_invalid_command(self):
        """测试无效命令处理"""
        from cli import main

        with patch('sys.argv', ['cli.py', 'invalid_command']):
            with self.assertRaises(SystemExit):
                main()


def run_tests():
    """运行所有测试"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # 添加所有测试类
    suite.addTests(loader.loadTestsFromTestCase(TestCLIHelp))
    suite.addTests(loader.loadTestsFromTestCase(TestAnalyzeCommand))
    suite.addTests(loader.loadTestsFromTestCase(TestDownloadCommand))
    suite.addTests(loader.loadTestsFromTestCase(TestDanmakuCommand))
    suite.addTests(loader.loadTestsFromTestCase(TestSubtitleCommand))
    suite.addTests(loader.loadTestsFromTestCase(TestClipCommand))
    suite.addTests(loader.loadTestsFromTestCase(TestScriptCommand))
    suite.addTests(loader.loadTestsFromTestCase(TestErrorHandling))

    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
