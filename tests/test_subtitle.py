#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SubtitleProcessor 模块单元测试

测试范围:
1. 字幕加载
2. SRT 格式转换
3. Markdown 格式转换
4. 片段字幕提取
5. 时间戳格式化
6. 字幕文件合并
"""

import unittest
import json
import os
import sys
import tempfile
import shutil

# 添加 src 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from subtitle import SubtitleProcessor


class TestSubtitleProcessorInit(unittest.TestCase):
    """测试 SubtitleProcessor 初始化"""

    def test_init_empty(self):
        """测试空初始化"""
        processor = SubtitleProcessor()
        self.assertIsNone(processor.json_file)
        self.assertIsNone(processor.data)

    def test_init_with_file(self):
        """测试使用文件初始化"""
        # 创建临时字幕文件
        temp_dir = tempfile.mkdtemp()
        json_file = os.path.join(temp_dir, "test_subtitle.json")

        test_data = {"body": [{"from": 0, "to": 1, "content": "测试"}]}
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(test_data, f)

        try:
            processor = SubtitleProcessor(json_file)
            self.assertEqual(processor.json_file, json_file)
            self.assertIsNotNone(processor.data)
            self.assertEqual(len(processor.data["body"]), 1)
        finally:
            shutil.rmtree(temp_dir)

    def test_init_with_nonexistent_file(self):
        """测试使用不存在的文件初始化"""
        processor = SubtitleProcessor("./nonexistent.json")
        self.assertIsNone(processor.data)


class TestFormatTimestamp(unittest.TestCase):
    """测试时间戳格式化"""

    def test_format_srt_basic(self):
        """测试基本 SRT 格式"""
        result = SubtitleProcessor.format_timestamp(1.5, srt_format=True)
        self.assertEqual(result, "00:00:01,500")

    def test_format_srt_minutes(self):
        """测试分钟级时间"""
        result = SubtitleProcessor.format_timestamp(65.123, srt_format=True)
        self.assertEqual(result, "00:01:05,123")

    def test_format_srt_hours(self):
        """测试小时级时间"""
        result = SubtitleProcessor.format_timestamp(3661.999, srt_format=True)
        # 由于浮点精度，最后一位可能有差异
        self.assertIn("01:01:01,", result)

    def test_format_vtt_format(self):
        """测试 VTT 格式（点毫秒）"""
        result = SubtitleProcessor.format_timestamp(1.5, srt_format=False)
        self.assertEqual(result, "00:00:01.500")

    def test_format_zero(self):
        """测试零时间"""
        result = SubtitleProcessor.format_timestamp(0, srt_format=True)
        self.assertEqual(result, "00:00:00,000")

    def test_format_edge_case(self):
        """测试边界情况"""
        # 999 毫秒
        result = SubtitleProcessor.format_timestamp(0.999, srt_format=True)
        self.assertEqual(result, "00:00:00,999")

    def test_format_vtt_format(self):
        """测试 VTT 格式（点毫秒）"""
        result = SubtitleProcessor.format_timestamp(1.5, srt_format=False)
        self.assertEqual(result, "00:00:01.500")

    def test_format_zero(self):
        """测试零时间"""
        result = SubtitleProcessor.format_timestamp(0, srt_format=True)
        self.assertEqual(result, "00:00:00,000")

    def test_format_edge_case(self):
        """测试边界情况"""
        # 999 毫秒
        result = SubtitleProcessor.format_timestamp(0.999, srt_format=True)
        self.assertEqual(result, "00:00:00,999")


class TestToSRT(unittest.TestCase):
    """测试 SRT 转换"""

    def setUp(self):
        """准备测试数据"""
        self.test_data = {
            "body": [
                {"from": 0.0, "to": 2.5, "content": "第一句"},
                {"from": 2.5, "to": 5.0, "content": "第二句"},
                {"from": 5.0, "to": 8.0, "content": "第三句"}
            ]
        }
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """清理临时文件"""
        shutil.rmtree(self.temp_dir)

    def test_to_srt_basic(self):
        """测试基本 SRT 转换"""
        processor = SubtitleProcessor()
        processor.data = self.test_data

        output_path = os.path.join(self.temp_dir, "output.srt")
        count = processor.to_srt(output_path)

        self.assertEqual(count, 3)
        self.assertTrue(os.path.exists(output_path))

        # 验证内容
        with open(output_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("1", content)
        self.assertIn("00:00:00,000 --> 00:00:02,500", content)
        self.assertIn("第一句", content)
        self.assertIn("第三句", content)

    def test_to_srt_empty_data(self):
        """测试空数据"""
        processor = SubtitleProcessor()
        processor.data = {"body": []}

        output_path = os.path.join(self.temp_dir, "empty.srt")
        count = processor.to_srt(output_path)

        self.assertEqual(count, 0)

    def test_to_srt_no_data(self):
        """测试未加载数据"""
        processor = SubtitleProcessor()

        with self.assertRaises(ValueError):
            processor.to_srt("./output.srt")

    def test_to_srt_whitespace(self):
        """测试空白字符处理"""
        processor = SubtitleProcessor()
        processor.data = {
            "body": [
                {"from": 0.0, "to": 1.0, "content": "  去空白  \n"}
            ]
        }

        output_path = os.path.join(self.temp_dir, "trim.srt")
        processor.to_srt(output_path)

        with open(output_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("去空白", content)


class TestToMarkdown(unittest.TestCase):
    """测试 Markdown 转换"""

    def setUp(self):
        """准备测试数据"""
        self.test_data = {
            "body": [
                {"from": 0.0, "to": 2.0, "content": "0 分钟内容"},
                {"from": 30.0, "to": 32.0, "content": "0 分钟内容 2"},
                {"from": 65.0, "to": 67.0, "content": "1 分钟内容"},
                {"from": 90.0, "to": 92.0, "content": "1 分钟内容 2"},
                {"from": 125.0, "to": 127.0, "content": "2 分钟内容"},
            ]
        }
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """清理临时文件"""
        shutil.rmtree(self.temp_dir)

    def test_to_markdown_basic(self):
        """测试基本 Markdown 转换"""
        processor = SubtitleProcessor()
        processor.data = self.test_data

        output_path = os.path.join(self.temp_dir, "output.md")
        count = processor.to_markdown(output_path, title="测试字幕")

        self.assertEqual(count, 5)
        self.assertTrue(os.path.exists(output_path))

        with open(output_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("# 测试字幕", content)
        self.assertIn("## 0:00 - 1:00", content)
        self.assertIn("## 1:00 - 2:00", content)
        self.assertIn("[0:00] 0 分钟内容", content)
        self.assertIn("[1:05] 1 分钟内容", content)

    def test_to_markdown_with_video_info(self):
        """测试带视频信息的 Markdown 转换"""
        processor = SubtitleProcessor()
        processor.data = self.test_data

        video_info = {
            "bvid": "BV1234567890",
            "owner": {"name": "测试 UP 主"}
        }

        output_path = os.path.join(self.temp_dir, "with_info.md")
        processor.to_markdown(output_path, video_info=video_info)

        with open(output_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("**BV 号**: BV1234567890", content)
        self.assertIn("**UP 主**: 测试 UP 主", content)


class TestExtractClip(unittest.TestCase):
    """测试片段字幕提取"""

    def setUp(self):
        """准备测试数据"""
        self.test_data = {
            "body": [
                {"from": 0.0, "to": 2.0, "content": "0-2 秒"},
                {"from": 5.0, "to": 7.0, "content": "5-7 秒"},
                {"from": 10.0, "to": 12.0, "content": "10-12 秒"},
                {"from": 15.0, "to": 17.0, "content": "15-17 秒"},
                {"from": 20.0, "to": 22.0, "content": "20-22 秒"},
            ]
        }

    def test_extract_clip_basic(self):
        """测试基本片段提取"""
        processor = SubtitleProcessor()
        processor.data = self.test_data

        clips = processor.extract_clip(start_sec=5.0, end_sec=15.0)

        self.assertEqual(len(clips), 2)
        self.assertEqual(clips[0]["content"], "5-7 秒")
        self.assertEqual(clips[1]["content"], "10-12 秒")

    def test_extract_clip_adjust_time(self):
        """测试时间调整"""
        processor = SubtitleProcessor()
        processor.data = self.test_data

        clips = processor.extract_clip(start_sec=5.0, end_sec=15.0, adjust_time=True)

        # 时间应该相对于片段开始调整
        self.assertEqual(clips[0]["from"], 0.0)  # 5-5=0
        self.assertEqual(clips[0]["to"], 2.0)    # 7-5=2

    def test_extract_clip_no_adjust(self):
        """测试不调整时间"""
        processor = SubtitleProcessor()
        processor.data = self.test_data

        clips = processor.extract_clip(start_sec=5.0, end_sec=15.0, adjust_time=False)

        # 时间保持原样
        self.assertEqual(clips[0]["from"], 5.0)
        self.assertEqual(clips[0]["to"], 7.0)

    def test_extract_clip_empty(self):
        """测试空结果"""
        processor = SubtitleProcessor()
        processor.data = self.test_data

        clips = processor.extract_clip(start_sec=100.0, end_sec=110.0)
        self.assertEqual(clips, [])

    def test_extract_clip_no_data(self):
        """测试未加载数据"""
        processor = SubtitleProcessor()

        with self.assertRaises(ValueError):
            processor.extract_clip(0, 10)


class TestSaveClip(unittest.TestCase):
    """测试片段字幕保存"""

    def setUp(self):
        """准备测试数据"""
        self.test_data = {
            "body": [
                {"from": 0.0, "to": 2.0, "content": "0-2 秒"},
                {"from": 5.0, "to": 7.0, "content": "5-7 秒"},
                {"from": 10.0, "to": 12.0, "content": "10-12 秒"},
            ]
        }
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """清理临时文件"""
        shutil.rmtree(self.temp_dir)

    def test_save_clip_basic(self):
        """测试基本片段保存"""
        processor = SubtitleProcessor()
        processor.data = self.test_data

        srt_path, md_path, count = processor.save_clip(
            start_sec=5.0, end_sec=12.0,
            output_dir=self.temp_dir,
            name="test_clip"
        )

        self.assertEqual(count, 2)
        self.assertIsNotNone(srt_path)
        self.assertIsNotNone(md_path)
        self.assertTrue(os.path.exists(srt_path))
        self.assertTrue(os.path.exists(md_path))

    def test_save_clip_empty(self):
        """测试空片段"""
        processor = SubtitleProcessor()
        processor.data = self.test_data

        srt_path, md_path, count = processor.save_clip(
            start_sec=100.0, end_sec=110.0,
            output_dir=self.temp_dir,
            name="empty_clip"
        )

        self.assertEqual(count, 0)
        self.assertIsNone(srt_path)
        self.assertIsNone(md_path)


class TestMergeSRT(unittest.TestCase):
    """测试 SRT 文件合并"""

    def setUp(self):
        """准备测试数据"""
        self.temp_dir = tempfile.mkdtemp()

        # 创建多个测试 SRT 文件
        self.srt_files = []
        for i in range(3):
            content = f"""1
00:00:00,000 --> 00:00:02,000
字幕{i+1}-1

2
00:00:02,000 --> 00:00:04,000
字幕{i+1}-2

"""
            # 使用字母前缀确保排序正确
            filepath = os.path.join(self.temp_dir, f"a{i:02d}_clip.srt")
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            self.srt_files.append(filepath)

    def tearDown(self):
        """清理临时文件"""
        shutil.rmtree(self.temp_dir)

    def test_merge_srt_basic(self):
        """测试基本合并"""
        output_path = os.path.join(self.temp_dir, "merged.srt")
        count = SubtitleProcessor.merge_srt_files(self.temp_dir, output_path)

        self.assertEqual(count, 6)  # 3 个文件 x 2 条字幕

        # 验证合并后的内容
        with open(output_path, "r", encoding="utf-8") as f:
            content = f.read()

        # 验证序号重排
        self.assertIn("1\n", content)
        self.assertIn("6\n", content)
        # 验证有 6 个字幕条目
        self.assertEqual(content.count("-->"), 6)

    def test_merge_srt_empty_dir(self):
        """测试空目录"""
        empty_dir = tempfile.mkdtemp()
        try:
            output_path = os.path.join(empty_dir, "merged.srt")
            count = SubtitleProcessor.merge_srt_files(empty_dir, output_path)
            self.assertEqual(count, 0)
        finally:
            shutil.rmtree(empty_dir)


class TestLoadFromFile(unittest.TestCase):
    """测试从文件加载"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_load_valid_file(self):
        """测试加载有效文件"""
        test_data = {
            "body": [
                {"from": 0, "to": 1, "content": "测试"}
            ]
        }
        json_file = os.path.join(self.temp_dir, "test.json")
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(test_data, f)

        processor = SubtitleProcessor()
        loaded = processor.load(json_file)

        self.assertEqual(len(loaded["body"]), 1)
        self.assertEqual(processor.data, loaded)

    def test_load_invalid_json(self):
        """测试加载无效 JSON"""
        json_file = os.path.join(self.temp_dir, "invalid.json")
        with open(json_file, "w", encoding="utf-8") as f:
            f.write("{invalid json}")

        processor = SubtitleProcessor()
        with self.assertRaises(json.JSONDecodeError):
            processor.load(json_file)


def run_tests():
    """运行所有测试"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # 添加所有测试类
    suite.addTests(loader.loadTestsFromTestCase(TestSubtitleProcessorInit))
    suite.addTests(loader.loadTestsFromTestCase(TestFormatTimestamp))
    suite.addTests(loader.loadTestsFromTestCase(TestToSRT))
    suite.addTests(loader.loadTestsFromTestCase(TestToMarkdown))
    suite.addTests(loader.loadTestsFromTestCase(TestExtractClip))
    suite.addTests(loader.loadTestsFromTestCase(TestSaveClip))
    suite.addTests(loader.loadTestsFromTestCase(TestMergeSRT))
    suite.addTests(loader.loadTestsFromTestCase(TestLoadFromFile))

    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
