#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
视频切分模块

功能：
1. 根据时间点切分视频片段
2. 批量切分多个片段
3. 自动生成 FFmpeg 命令
"""

import os
import subprocess
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass


@dataclass
class VideoClip:
    """视频片段定义"""
    name: str
    start: float  # 开始时间（秒）
    duration: float  # 持续时间（秒）
    description: str = ""


class VideoClipper:
    """视频切分器"""

    def __init__(self, input_video: str, output_dir: str = "clips"):
        """初始化

        Args:
            input_video: 输入视频文件路径
            output_dir: 输出目录
        """
        self.input_video = input_video
        self.output_dir = output_dir
        self.clips: List[VideoClip] = []

        if not os.path.exists(input_video):
            raise FileNotFoundError(f"视频文件不存在：{input_video}")

    def add_clip(self, name: str, start: float, duration: float,
                 description: str = "") -> "VideoClipper":
        """添加切分片段

        Args:
            name: 片段名称
            start: 开始时间（秒）
            duration: 持续时间（秒）
            description: 片段描述

        Returns:
            self，支持链式调用
        """
        self.clips.append(VideoClip(name, start, duration, description))
        return self

    def add_clips_from_list(self, clips: List[Tuple[str, float, float, str]]) -> "VideoClipper":
        """批量添加切分片段

        Args:
            clips: 列表，每个元素为 (name, start, duration, description)

        Returns:
            self，支持链式调用
        """
        for clip in clips:
            if len(clip) == 3:
                name, start, duration = clip
                description = ""
            else:
                name, start, duration, description = clip
            self.clips.append(VideoClip(name, start, duration, description))
        return self

    @staticmethod
    def format_time(seconds: float) -> str:
        """格式化时间为 HH:MM:SS.mmm"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{secs:06.3f}"

    def check_ffmpeg(self) -> bool:
        """检查是否安装了 ffmpeg"""
        try:
            subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def split_clip(self, clip: VideoClip, output_path: Optional[str] = None) -> str:
        """切分单个片段

        Args:
            clip: 视频片段定义
            output_path: 输出文件路径（可选）

        Returns:
            输出文件路径
        """
        if not output_path:
            os.makedirs(self.output_dir, exist_ok=True)
            output_path = os.path.join(self.output_dir, f"{clip.name}.mp4")

        cmd = [
            "ffmpeg", "-y",
            "-i", self.input_video,
            "-ss", self.format_time(clip.start),
            "-t", f"{clip.duration:.3f}",
            "-c", "copy",
            output_path
        ]

        print(f"切分：{clip.name} ({self.format_time(clip.start)} - {self.format_time(clip.start + clip.duration)})")

        try:
            subprocess.run(cmd, capture_output=True, check=True)
            print(f"  ✅ {output_path}")
            return output_path
        except subprocess.CalledProcessError as e:
            print(f"  ❌ 失败：{e.stderr.decode() if e.stderr else e}")
            raise

    def split_all(self) -> List[str]:
        """切分所有片段

        Returns:
            输出文件路径列表
        """
        if not self.check_ffmpeg():
            raise RuntimeError("未找到 ffmpeg，请先安装")

        os.makedirs(self.output_dir, exist_ok=True)

        output_paths = []
        for clip in self.clips:
            output_path = os.path.join(self.output_dir, f"{clip.name}.mp4")
            self.split_clip(clip, output_path)
            output_paths.append(output_path)

        print(f"\n✅ 完成！共切分 {len(self.clips)} 个片段到：{self.output_dir}/")
        return output_paths

    def generate_script(self, output_path: str = "split_video.sh") -> str:
        """生成 Shell 脚本

        Args:
            output_path: 脚本输出路径

        Returns:
            脚本内容
        """
        script = """#!/bin/bash
# 视频切分脚本 - 由 bilibili-analyzer 生成

VIDEO="{}"
OUTPUT_DIR="{}"

# 创建输出目录
mkdir -p "$OUTPUT_DIR"

echo "开始切分视频：$VIDEO"
echo "输出目录：$OUTPUT_DIR"
echo ""

""".format(self.input_video, self.output_dir)

        for clip in self.clips:
            desc = f" - {clip.description}" if clip.description else ""
            script += f"""# {clip.name}{desc}
ffmpeg -y -i "$VIDEO" -ss {self.format_time(clip.start)} -t {clip.duration:.3f} -c copy "$OUTPUT_DIR/{clip.name}.mp4"
echo "✅ 切分完成：{clip.name}.mp4"

"""

        script += """
echo ""
echo "================================"
echo "视频切分完成！"
echo "================================"
"""

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(script)

        os.chmod(output_path, 0o755)
        print(f"✅ 脚本已生成：{output_path}")

        return script

    @classmethod
    def from_timeline(cls, input_video: str, output_dir: str,
                      timeline: List[Dict]) -> "VideoClipper":
        """从时间轴创建切分器

        Args:
            input_video: 输入视频文件路径
            output_dir: 输出目录
            timeline: 时间轴列表，每项包含 {name, start, duration, description}

        Returns:
            VideoClipper 实例
        """
        clipper = cls(input_video, output_dir)

        for item in timeline:
            clipper.add_clip(
                name=item["name"],
                start=item["start"],
                duration=item.get("duration", 30),
                description=item.get("description", "")
            )

        return clipper
