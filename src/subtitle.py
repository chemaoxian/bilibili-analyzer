#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
字幕处理模块

功能：
1. B 站 AI 字幕 JSON 转 SRT
2. B 站 AI 字幕 JSON 转 Markdown
3. 提取片段字幕
4. 合并字幕文件
"""

import json
import os
from typing import Dict, List, Optional


class SubtitleProcessor:
    """字幕处理器"""

    def __init__(self, json_file: Optional[str] = None):
        """初始化

        Args:
            json_file: B 站字幕 JSON 文件路径
        """
        self.json_file = json_file
        self.data: Optional[Dict] = None

        if json_file and os.path.exists(json_file):
            self.load(json_file)

    def load(self, json_file: str) -> Dict:
        """加载字幕 JSON 文件"""
        with open(json_file, "r", encoding="utf-8") as f:
            self.data = json.load(f)
        return self.data

    @staticmethod
    def format_timestamp(seconds: float, srt_format: bool = True) -> str:
        """格式化时间为 SRT 格式

        Args:
            seconds: 秒数
            srt_format: True 为 SRT 格式 (逗号毫秒), False 为 VTT 格式 (点毫秒)

        Returns:
            格式化后的时间字符串
        """
        millis = int((seconds % 1) * 1000)
        total_seconds = int(seconds)
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        secs = total_seconds % 60

        if srt_format:
            return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
        else:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"

    def to_srt(self, output_path: str, language: Optional[str] = None) -> int:
        """转换为 SRT 字幕文件

        Args:
            output_path: 输出文件路径
            language: 指定字幕语言（如果有多个语言）

        Returns:
            字幕条数
        """
        if not self.data:
            raise ValueError("未加载字幕数据")

        body = self.data.get("body", [])

        # 如果有多个语言，筛选指定语言
        if language:
            subtitles = self.data.get("subtitles", [])
            for sub in subtitles:
                if sub.get("language") == language:
                    body = sub.get("content", [])
                    break

        count = 0
        with open(output_path, "w", encoding="utf-8") as f:
            for i, item in enumerate(body, 1):
                start = self.format_timestamp(item["from"])
                end = self.format_timestamp(item["to"])
                content = item["content"].strip()

                f.write(f"{i}\n")
                f.write(f"{start} --> {end}\n")
                f.write(f"{content}\n\n")
                count += 1

        return count

    def to_markdown(self, output_path: str, title: str = "视频字幕",
                    video_info: Optional[Dict] = None) -> int:
        """转换为 Markdown 格式

        Args:
            output_path: 输出文件路径
            title: 标题
            video_info: 视频基本信息（可选）

        Returns:
            字幕条数
        """
        if not self.data:
            raise ValueError("未加载字幕数据")

        body = self.data.get("body", [])
        count = len(body)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(f"# {title}\n\n")

            if video_info:
                f.write(f"**BV 号**: {video_info.get('bvid', 'N/A')}\n")
                f.write(f"**UP 主**: {video_info.get('owner', {}).get('name', 'N/A')}\n")
                f.write(f"**字幕片段数**: {len(body)}\n\n")
            else:
                f.write(f"**字幕片段数**: {len(body)}\n\n")

            f.write("---\n\n")

            # 按分钟分组
            current_minute = -1

            for item in body:
                from_sec = item["from"]
                to_sec = item["to"]
                content = item["content"].strip()

                minute = int(from_sec // 60)
                if minute != current_minute:
                    current_minute = minute
                    f.write(f"\n## {minute}:00 - {minute + 1}:00\n\n")

                time_str = f"{int(from_sec // 60)}:{int(from_sec % 60):02d}"
                f.write(f"- [{time_str}] {content}\n")

        return count

    def extract_clip(self, start_sec: float, end_sec: float,
                     adjust_time: bool = True) -> List[Dict]:
        """提取指定时间段的字幕

        Args:
            start_sec: 开始时间（秒）
            end_sec: 结束时间（秒）
            adjust_time: 是否调整时间戳（相对于片段开始）

        Returns:
            提取的字幕列表
        """
        if not self.data:
            raise ValueError("未加载字幕数据")

        body = self.data.get("body", [])

        # 筛选时间段内的字幕
        clip_subs = [
            item for item in body
            if item["from"] >= start_sec and item["to"] <= end_sec
        ]

        # 调整时间戳
        if adjust_time:
            adjusted_subs = []
            for item in clip_subs:
                adjusted_subs.append({
                    "from": item["from"] - start_sec,
                    "to": item["to"] - start_sec,
                    "content": item["content"]
                })
            return adjusted_subs

        return clip_subs

    def save_clip(self, start_sec: float, end_sec: float, output_dir: str,
                  name: str, adjust_time: bool = True) -> tuple:
        """提取并保存片段字幕

        Args:
            start_sec: 开始时间（秒）
            end_sec: 结束时间（秒）
            output_dir: 输出目录
            name: 输出文件名前缀
            adjust_time: 是否调整时间戳

        Returns:
            (srt_path, md_path, count) 或 (None, None, 0)
        """
        clip_subs = self.extract_clip(start_sec, end_sec, adjust_time)

        if not clip_subs:
            return None, None, 0

        os.makedirs(output_dir, exist_ok=True)

        # 保存 SRT
        srt_path = os.path.join(output_dir, f"{name}.srt")
        with open(srt_path, "w", encoding="utf-8") as f:
            for i, item in enumerate(clip_subs, 1):
                start = self.format_timestamp(item["from"])
                end = self.format_timestamp(item["to"])
                content = item["content"].strip()
                f.write(f"{i}\n")
                f.write(f"{start} --> {end}\n")
                f.write(f"{content}\n\n")

        # 保存 Markdown
        md_path = os.path.join(output_dir, f"{name}_subtitle.md")
        time_display = f"{int(start_sec // 60)}:{int(start_sec % 60):02d} - {int(end_sec // 60)}:{int(end_sec % 60):02d}"

        with open(md_path, "w", encoding="utf-8") as f:
            f.write(f"# 视频片段字幕\n\n")
            f.write(f"**时间段**: {time_display}\n\n")
            for item in clip_subs:
                time_str = f"{int(item['from'] // 60)}:{int(item['from'] % 60):02d}"
                f.write(f"- [{time_str}] {item['content']}\n")

        return srt_path, md_path, len(clip_subs)

    @staticmethod
    def merge_srt_files(input_dir: str, output_path: str) -> int:
        """合并多个 SRT 文件

        Args:
            input_dir: 包含 SRT 文件的目录
            output_path: 输出文件路径

        Returns:
            合并后的字幕条数
        """
        srt_files = sorted([f for f in os.listdir(input_dir) if f.endswith(".srt")
                           and not f.startswith("merged")])

        total_count = 0
        current_index = 1

        with open(output_path, "w", encoding="utf-8") as f:
            for filename in srt_files:
                filepath = os.path.join(input_dir, filename)
                with open(filepath, "r", encoding="utf-8") as sf:
                    content = sf.read().strip()
                    blocks = content.split("\n\n")

                    for block in blocks:
                        lines = block.strip().split("\n")
                        if len(lines) >= 3:
                            # 重写序号
                            f.write(f"{current_index}\n")
                            f.write(f"{lines[1]}\n")
                            f.write(f"{lines[2]}\n\n")
                            current_index += 1
                            total_count += 1

        return total_count
