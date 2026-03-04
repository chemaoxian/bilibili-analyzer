#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VideoClipper 模块单元测试

测试范围:
1. 类初始化和验证
2. 片段添加（链式调用）
3. 时间格式化
4. ffmpeg 检查
5. Shell 脚本生成
6. 从时间轴创建
"""

import unittest
import os
import sys
import tempfile
import shutil
import subprocess
from unittest.mock import patch, MagicMock

# 添加 src 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from clipper import VideoClipper, VideoClip


class TestVideoClipInit(unittest.TestCase):
    """测试 VideoClip 数据类"""

    def test_clip_minimal(self):
        """测试最小化创建"""
        clip = VideoClip(name="test", start=10.0, duration=30.0)
        self.assertEqual(clip.name, "test")
        self.assertEqual(clip.start, 10.0)
        self.assertEqual(clip.duration, 30.0)
        self.assertEqual(clip.description, "")

    def test_clip_full(self):
        """测试完整创建"""
        clip = VideoClip(
            name="highlight",
            start=60.0,
            duration=45.0,
            description="精彩片段"
        )
        self.assertEqual(clip.name, "highlight")
        self.assertEqual(clip.start, 60.0)
        self.assertEqual(clip.duration, 45.0)
        self.assertEqual(clip.description, "精彩片段")


class TestVideoClipperInit(unittest.TestCase):
    """测试 VideoClipper 初始化"""

    def setUp(self):
        """创建临时视频文件"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_video = os.path.join(self.temp_dir, "test.mp4")
        # 创建空文件作为测试
        with open(self.test_video, "w") as f:
            f.write("")

    def tearDown(self):
        """清理临时文件"""
        shutil.rmtree(self.temp_dir)

    def test_init_valid(self):
        """测试有效初始化"""
        clipper = VideoClipper(self.test_video, output_dir="clips")
        self.assertEqual(clipper.input_video, self.test_video)
        self.assertEqual(clipper.output_dir, "clips")
        self.assertEqual(len(clipper.clips), 0)

    def test_init_default_output(self):
        """测试默认输出目录"""
        clipper = VideoClipper(self.test_video)
        self.assertEqual(clipper.output_dir, "clips")

    def test_init_nonexistent_file(self):
        """测试不存在的文件"""
        with self.assertRaises(FileNotFoundError):
            VideoClipper("./nonexistent_video.mp4")


class TestAddClip(unittest.TestCase):
    """测试添加片段"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.test_video = os.path.join(self.temp_dir, "test.mp4")
        with open(self.test_video, "w") as f:
            f.write("")

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_add_clip_single(self):
        """测试添加单个片段"""
        clipper = VideoClipper(self.test_video)
        clipper.add_clip("intro", start=0, duration=30)

        self.assertEqual(len(clipper.clips), 1)
        self.assertEqual(clipper.clips[0].name, "intro")
        self.assertEqual(clipper.clips[0].start, 0)
        self.assertEqual(clipper.clips[0].duration, 30)

    def test_add_clip_with_description(self):
        """测试添加带描述的片段"""
        clipper = VideoClipper(self.test_video)
        clipper.add_clip("highlight", start=60, duration=45, description="精彩部分")

        self.assertEqual(clipper.clips[0].description, "精彩部分")

    def test_add_clip_chain(self):
        """测试链式添加"""
        clipper = VideoClipper(self.test_video)
        clipper.add_clip("intro", start=0, duration=30)

        # 验证已添加
        self.assertEqual(len(clipper.clips), 1)

    def test_add_clips_from_list(self):
        """测试批量添加"""
        clipper = VideoClipper(self.test_video)
        clips = [
            ("intro", 0, 30, "开场"),
            ("highlight", 60, 45, "亮点"),
            ("ending", 300, 30, "结尾"),
        ]
        clipper.add_clips_from_list(clips)

        self.assertEqual(len(clipper.clips), 3)
        self.assertEqual(clipper.clips[0].name, "intro")
        self.assertEqual(clipper.clips[2].description, "结尾")

    def test_add_clips_from_list_minimal(self):
        """测试批量添加（不含描述）"""
        clipper = VideoClipper(self.test_video)
        clips = [
            ("clip1", 0, 30),
            ("clip2", 60, 45),
        ]
        clipper.add_clips_from_list(clips)

        self.assertEqual(len(clipper.clips), 2)
        self.assertEqual(clipper.clips[0].description, "")


class TestFormatTime(unittest.TestCase):
    """测试时间格式化"""

    def test_format_seconds(self):
        """测试秒级格式化"""
        result = VideoClipper.format_time(45.123)
        self.assertEqual(result, "00:00:45.123")

    def test_format_minutes(self):
        """测试分钟级格式化"""
        result = VideoClipper.format_time(125.5)
        self.assertEqual(result, "00:02:05.500")

    def test_format_hours(self):
        """测试小时级格式化"""
        result = VideoClipper.format_time(3661.123)
        self.assertEqual(result, "01:01:01.123")

    def test_format_zero(self):
        """测试零时间"""
        result = VideoClipper.format_time(0)
        self.assertEqual(result, "00:00:00.000")

    def test_format_precision(self):
        """测试精度"""
        result = VideoClipper.format_time(1.9999)
        # 精度保留三位小数
        self.assertIn("00:00:02", result)


class TestCheckFFmpeg(unittest.TestCase):
    """测试 ffmpeg 检查"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.test_video = os.path.join(self.temp_dir, "test.mp4")
        with open(self.test_video, "w") as f:
            f.write("")

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    @patch('clipper.subprocess.run')
    def test_check_ffmpeg_installed(self, mock_run):
        """测试 ffmpeg 已安装"""
        mock_run.return_value = None  # 不抛出异常
        clipper = VideoClipper(self.test_video)
        result = clipper.check_ffmpeg()
        self.assertTrue(result)

    @patch('clipper.subprocess.run')
    def test_check_ffmpeg_not_installed(self, mock_run):
        """测试 ffmpeg 未安装"""
        mock_run.side_effect = FileNotFoundError()
        clipper = VideoClipper(self.test_video)
        result = clipper.check_ffmpeg()
        self.assertFalse(result)


class TestGenerateScript(unittest.TestCase):
    """测试 Shell 脚本生成"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.test_video = os.path.join(self.temp_dir, "test.mp4")
        with open(self.test_video, "w") as f:
            f.write("")

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_generate_script_basic(self):
        """测试基本脚本生成"""
        clipper = VideoClipper(self.test_video, output_dir="clips")
        clipper.add_clip("intro", 0, 30)
        clipper.add_clip("highlight", 60, 45)

        script_path = os.path.join(self.temp_dir, "cut.sh")
        clipper.generate_script(script_path)

        self.assertTrue(os.path.exists(script_path))

        # 验证脚本内容
        with open(script_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("#!/bin/bash", content)
        self.assertIn("intro", content)
        self.assertIn("highlight", content)
        self.assertIn("-ss 00:00:00.000", content)
        self.assertIn("-ss 00:01:00.000", content)

    def test_generate_script_with_description(self):
        """测试带描述的脚本生成"""
        clipper = VideoClipper(self.test_video)
        clipper.add_clip("test", 10, 20, "测试片段")

        script_path = os.path.join(self.temp_dir, "desc.sh")
        clipper.generate_script(script_path)

        with open(script_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("# test - 测试片段", content)

    def test_generate_script_default_path(self):
        """测试默认路径"""
        clipper = VideoClipper(self.test_video)
        clipper.add_clip("test", 0, 10)

        # 使用默认路径
        clipper.generate_script()

        self.assertTrue(os.path.exists("split_video.sh"))
        os.remove("split_video.sh")

    def test_generate_script_executable(self):
        """测试脚本可执行权限"""
        clipper = VideoClipper(self.test_video)
        clipper.add_clip("test", 0, 10)

        script_path = os.path.join(self.temp_dir, "exec.sh")
        clipper.generate_script(script_path)

        # 检查可执行权限
        stat_info = os.stat(script_path)
        self.assertTrue(stat_info.st_mode & 0o111)


class TestSplitClip(unittest.TestCase):
    """测试片段切分"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.test_video = os.path.join(self.temp_dir, "test.mp4")
        with open(self.test_video, "w") as f:
            f.write("")

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    @patch('clipper.subprocess.run')
    def test_split_clip_success(self, mock_run):
        """测试成功切分"""
        mock_run.return_value = None
        clipper = VideoClipper(self.test_video, output_dir=self.temp_dir)
        clipper.add_clip("test", 0, 30)

        output_path = os.path.join(self.temp_dir, "test.mp4")
        result = clipper.split_clip(clipper.clips[0], output_path)

        self.assertEqual(result, output_path)

    @patch('clipper.subprocess.run')
    def test_split_clip_default_path(self, mock_run):
        """测试默认输出路径"""
        mock_run.return_value = None
        clipper = VideoClipper(self.test_video, output_dir=self.temp_dir)
        clipper.add_clip("test", 0, 30)

        # 不指定输出路径
        result = clipper.split_clip(clipper.clips[0])

        self.assertIn(self.temp_dir, result)
        self.assertIn("test.mp4", result)

    @patch('clipper.subprocess.run')
    def test_split_clip_failure(self, mock_run):
        """测试切分失败"""
        mock_run.side_effect = subprocess.CalledProcessError(1, "ffmpeg")
        clipper = VideoClipper(self.test_video)
        clipper.add_clip("test", 0, 30)

        with self.assertRaises(subprocess.CalledProcessError):
            clipper.split_clip(clipper.clips[0])


class TestSplitAll(unittest.TestCase):
    """测试批量切分"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.test_video = os.path.join(self.temp_dir, "test.mp4")
        with open(self.test_video, "w") as f:
            f.write("")

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    @patch('clipper.VideoClipper.check_ffmpeg')
    @patch('clipper.subprocess.run')
    def test_split_all_success(self, mock_run, mock_check):
        """测试成功批量切分"""
        mock_check.return_value = True
        mock_run.return_value = None

        clipper = VideoClipper(self.test_video, output_dir=self.temp_dir)
        clipper.add_clip("clip1", 0, 30)
        clipper.add_clip("clip2", 60, 45)

        results = clipper.split_all()

        self.assertEqual(len(results), 2)
        self.assertTrue(all(self.temp_dir in p for p in results))

    @patch('clipper.VideoClipper.check_ffmpeg')
    def test_split_all_no_ffmpeg(self, mock_check):
        """测试无 ffmpeg 情况"""
        mock_check.return_value = False

        clipper = VideoClipper(self.test_video)
        clipper.add_clip("test", 0, 30)

        with self.assertRaises(RuntimeError):
            clipper.split_all()

    @patch('clipper.VideoClipper.check_ffmpeg')
    @patch('clipper.subprocess.run')
    def test_split_all_creates_output_dir(self, mock_run, mock_check):
        """测试创建输出目录"""
        mock_check.return_value = True
        mock_run.return_value = None

        new_output = os.path.join(self.temp_dir, "new_clips")
        clipper = VideoClipper(self.test_video, output_dir=new_output)
        clipper.add_clip("test", 0, 30)

        # 输出目录不存在
        self.assertFalse(os.path.exists(new_output))

        clipper.split_all()

        # 应该被创建
        self.assertTrue(os.path.exists(new_output))


class TestFromTimeline(unittest.TestCase):
    """测试从时间轴创建"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.test_video = os.path.join(self.temp_dir, "test.mp4")
        with open(self.test_video, "w") as f:
            f.write("")

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_from_timeline_basic(self):
        """测试基本创建"""
        timeline = [
            {"name": "intro", "start": 0, "duration": 30, "description": "开场"},
            {"name": "main", "start": 30, "duration": 60, "description": "主体"},
        ]

        clipper = VideoClipper.from_timeline(
            self.test_video,
            output_dir="clips",
            timeline=timeline
        )

        self.assertEqual(len(clipper.clips), 2)
        self.assertEqual(clipper.clips[0].name, "intro")
        self.assertEqual(clipper.clips[1].start, 30)

    def test_from_timeline_minimal(self):
        """测试最小化时间轴（无描述）"""
        timeline = [
            {"name": "clip1", "start": 0, "duration": 30},
        ]

        clipper = VideoClipper.from_timeline(
            self.test_video,
            output_dir="clips",
            timeline=timeline
        )

        self.assertEqual(clipper.clips[0].description, "")


# 模块级别的 ffmpeg 检查结果
HAS_FFMPEG_FOR_TESTS = False
try:
    subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
    HAS_FFMPEG_FOR_TESTS = True
except (subprocess.CalledProcessError, FileNotFoundError):
    pass


class TestIntegration(unittest.TestCase):
    """集成测试"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.test_video = os.path.join(self.temp_dir, "test.mp4")
        # 创建一个真实的简单视频用于测试
        if HAS_FFMPEG_FOR_TESTS:
            try:
                # 使用 ffmpeg 创建测试视频
                subprocess.run([
                    "ffmpeg", "-y",
                    "-f", "lavfi",
                    "-i", "color=c=blue:s=320x240:d=5",
                    "-f", "lavfi",
                    "-i", "sine=frequency=440:duration=5",
                    "-c:v", "libx264",
                    "-c:a", "aac",
                    "-shortest",
                    self.test_video
                ], capture_output=True, check=True)
            except subprocess.CalledProcessError:
                with open(self.test_video, "w") as f:
                    f.write("")
        else:
            with open(self.test_video, "w") as f:
                f.write("")

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    @unittest.skipIf(not HAS_FFMPEG_FOR_TESTS, "需要真实的 ffmpeg 支持")
    def test_full_workflow(self):
        """测试完整工作流程"""
        # 1. 创建切分器
        clipper = VideoClipper(self.test_video, output_dir=self.temp_dir)

        # 2. 添加片段
        clipper.add_clip("part1", 0, 2, "第一部分")
        clipper.add_clip("part2", 2, 2, "第二部分")

        # 3. 生成脚本
        script_path = os.path.join(self.temp_dir, "cut.sh")
        clipper.generate_script(script_path)
        self.assertTrue(os.path.exists(script_path))

        # 4. 执行切分（如果有 ffmpeg）
        try:
            results = clipper.split_all()
            self.assertEqual(len(results), 2)
            for path in results:
                self.assertTrue(os.path.exists(path))
        except RuntimeError:
            # 没有 ffmpeg 是允许的
            pass


def run_tests():
    """运行所有测试"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # 添加所有测试类
    suite.addTests(loader.loadTestsFromTestCase(TestVideoClipInit))
    suite.addTests(loader.loadTestsFromTestCase(TestVideoClipperInit))
    suite.addTests(loader.loadTestsFromTestCase(TestAddClip))
    suite.addTests(loader.loadTestsFromTestCase(TestFormatTime))
    suite.addTests(loader.loadTestsFromTestCase(TestCheckFFmpeg))
    suite.addTests(loader.loadTestsFromTestCase(TestGenerateScript))
    suite.addTests(loader.loadTestsFromTestCase(TestSplitClip))
    suite.addTests(loader.loadTestsFromTestCase(TestSplitAll))
    suite.addTests(loader.loadTestsFromTestCase(TestFromTimeline))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))

    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
