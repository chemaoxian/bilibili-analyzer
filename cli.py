#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
B 站视频分析工具 - 命令行入口

用法:
    python cli.py analyze BV1zZcYz1EMy      # 分析视频
    python cli.py download BV1zZcYz1EMy    # 下载视频
    python cli.py danmaku BV1zZcYz1EMy     # 提取弹幕
    python cli.py subtitle BV1zZcYz1EMy    # 提取字幕
    python cli.py clip BV1zZcYz1EMy        # 切分视频

Cookie 配置:
    默认从 .cache/credentials/bilibili-cookie.txt 读取
    或使用 -c/--cookie 参数指定
"""

import argparse
import sys
import os

# 添加 src 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from analyzer import BiliAnalyzer
from subtitle import SubtitleProcessor
from clipper import VideoClipper, VideoClip


# 默认 Cookie 路径（本地安全存储）
DEFAULT_COOKIE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    ".cache",
    "credentials",
    "bilibili-cookie.txt"
)


def get_cookie_file(cookie_arg):
    """获取 Cookie 文件路径

    优先级：命令行参数 > 默认路径 > None
    """
    if cookie_arg:
        return cookie_arg
    if os.path.exists(DEFAULT_COOKIE_PATH):
        return DEFAULT_COOKIE_PATH
    return None


def cmd_analyze(args):
    """分析视频命令"""
    cookie_file = get_cookie_file(args.cookie)
    analyzer = BiliAnalyzer(args.bv_id, cookie_file=cookie_file)
    analyzer.analyze(output_dir=args.output)


def cmd_download(args):
    """下载视频命令"""
    cookie_file = get_cookie_file(args.cookie)
    analyzer = BiliAnalyzer(args.bv_id, cookie_file=cookie_file)

    output = args.output or f"{args.bv_id}.mp4"
    if not analyzer.download_video(output):
        sys.exit(1)


def cmd_danmaku(args):
    """提取弹幕命令"""
    analyzer = BiliAnalyzer(args.bv_id)
    danmaku = analyzer.get_danmaku()

    output = args.output or f"{args.bv_id}_danmaku.json"
    import json
    with open(output, "w", encoding="utf-8") as f:
        json.dump(danmaku, f, ensure_ascii=False, indent=2)

    print(f"✅ 弹幕已保存到：{output}")
    print(f"   共 {len(danmaku)} 条")


def cmd_subtitle(args):
    """提取字幕命令"""
    analyzer = BiliAnalyzer(args.bv_id)
    subtitles = analyzer.get_subtitles()

    if not subtitles:
        print("⚠️  该视频暂无 CC 字幕")
        sys.exit(0)

    output_dir = args.output or "."
    os.makedirs(output_dir, exist_ok=True)

    for sub in subtitles:
        lang = sub["language"] or "zh"
        output = os.path.join(output_dir, f"{args.bv_id}_{lang}.srt")

        processor = SubtitleProcessor()
        processor.data = {"body": sub["content"]}
        count = processor.to_srt(output)

        print(f"✅ {lang} 字幕已保存到：{output} (共 {count} 条)")


def cmd_clip(args):
    """切分视频命令"""
    if not os.path.exists(args.input):
        print(f"❌ 视频文件不存在：{args.input}")
        sys.exit(1)

    clipper = VideoClipper(args.input, args.output)

    # 默认切分方案（30 秒一段）
    if not args.clips:
        # 从配置文件或默认值读取
        default_clips = [
            ("01_opening", 0, 30, "开场片段"),
            ("02_hotspot_30s-1m", 30, 30, "弹幕热点 1"),
            ("03_hotspot_1m-1m30s", 60, 30, "弹幕热点 2"),
            ("04_hotspot_2m30s-3m", 150, 30, "弹幕热点 3"),
            ("05_hotspot_3m-3m30s", 180, 30, "弹幕热点 4"),
            ("06_hotspot_5m-5m30s", 300, 30, "弹幕热点 5"),
            ("07_hotspot_ai_command", 330, 30, "AI 指挥人类"),
            ("08_hotspot_6m-6m30s", 360, 30, "弹幕热点 6"),
            ("09_hotspot_6m30s-7m", 390, 30, "弹幕热点 7"),
            ("10_hotspot_dependency", 420, 30, "依赖即被取代"),
        ]
        clipper.add_clips_from_list(default_clips)

    clipper.split_all()


def cmd_generate_script(args):
    """生成切分脚本命令"""
    if not os.path.exists(args.input):
        print(f"❌ 视频文件不存在：{args.input}")
        sys.exit(1)

    clipper = VideoClipper(args.input, args.output)

    # 默认切分方案
    default_clips = [
        ("01_opening", 0, 30, "开场片段"),
        ("02_hotspot_30s-1m", 30, 30, "弹幕热点 1"),
        ("03_hotspot_1m-1m30s", 60, 30, "弹幕热点 2"),
        ("04_hotspot_2m30s-3m", 150, 30, "弹幕热点 3"),
        ("05_hotspot_3m-3m30s", 180, 30, "弹幕热点 4"),
        ("06_hotspot_5m-5m30s", 300, 30, "弹幕热点 5"),
        ("07_hotspot_ai_command", 330, 30, "AI 指挥人类"),
        ("08_hotspot_6m-6m30s", 360, 30, "弹幕热点 6"),
        ("09_hotspot_6m30s-7m", 390, 30, "弹幕热点 7"),
        ("10_hotspot_dependency", 420, 30, "依赖即被取代"),
    ]
    clipper.add_clips_from_list(default_clips)

    clipper.generate_script(args.script or "split_video.sh")


def main():
    parser = argparse.ArgumentParser(
        description="B 站视频分析工具 - 分析、下载、提取弹幕字幕",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python cli.py analyze BV1zZcYz1EMy           # 分析视频
  python cli.py download BV1zZcYz1EMy -o v.mp4 # 下载视频
  python cli.py danmaku BV1zZcYz1EMy           # 提取弹幕
  python cli.py subtitle BV1zZcYz1EMy          # 提取字幕
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="命令")

    # analyze 命令
    p_analyze = subparsers.add_parser("analyze", help="分析视频，生成报告")
    p_analyze.add_argument("bv_id", help="BV 号，如 BV1zZcYz1EMy")
    p_analyze.add_argument("-o", "--output", default=".", help="输出目录")
    p_analyze.add_argument("-c", "--cookie", help="Cookie 文件路径（默认：.cache/credentials/bilibili-cookie.txt）")
    p_analyze.set_defaults(func=cmd_analyze)

    # download 命令
    p_download = subparsers.add_parser("download", help="下载视频")
    p_download.add_argument("bv_id", help="BV 号")
    p_download.add_argument("-o", "--output", help="输出文件路径")
    p_download.add_argument("-c", "--cookie", help="Cookie 文件路径（默认：.cache/credentials/bilibili-cookie.txt）")
    p_download.set_defaults(func=cmd_download)

    # danmaku 命令
    p_danmaku = subparsers.add_parser("danmaku", help="提取弹幕")
    p_danmaku.add_argument("bv_id", help="BV 号")
    p_danmaku.add_argument("-o", "--output", help="输出文件路径")
    p_danmaku.set_defaults(func=cmd_danmaku)

    # subtitle 命令
    p_subtitle = subparsers.add_parser("subtitle", help="提取字幕")
    p_subtitle.add_argument("bv_id", help="BV 号")
    p_subtitle.add_argument("-o", "--output", help="输出目录")
    p_subtitle.set_defaults(func=cmd_subtitle)

    # clip 命令
    p_clip = subparsers.add_parser("clip", help="切分视频片段")
    p_clip.add_argument("input", help="输入视频文件路径")
    p_clip.add_argument("-o", "--output", default="clips", help="输出目录")
    p_clip.add_argument("--clips", action="store_true", help="使用自定义切分方案")
    p_clip.set_defaults(func=cmd_clip)

    # script 命令
    p_script = subparsers.add_parser("script", help="生成切分脚本")
    p_script.add_argument("input", help="输入视频文件路径")
    p_script.add_argument("-o", "--output", default="clips", help="输出目录")
    p_script.add_argument("-s", "--script", default="split_video.sh", help="脚本输出路径")
    p_script.set_defaults(func=cmd_generate_script)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    try:
        args.func(args)
    except KeyboardInterrupt:
        print("\n❌ 用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 错误：{e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
