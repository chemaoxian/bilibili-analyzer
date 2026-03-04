"""
B 站视频分析工具
Bilibili Video Analyzer - Analyze Bilibili videos, extract danmaku, subtitles, and more.
"""

__version__ = "0.1.0"
__author__ = "AI 拥抱者"
__license__ = "MIT"

from .analyzer import BiliAnalyzer
from .subtitle import SubtitleProcessor
from .clipper import VideoClipper

__all__ = ["BiliAnalyzer", "SubtitleProcessor", "VideoClipper"]
