#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
B 站视频分析工具 - 使用示例

这个脚本展示了如何使用 bilibili-analyzer 的各个模块。
"""

import sys
import os

# 添加 src 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


def example_basic_analyze():
    """示例 1: 基础视频分析"""
    print("=" * 60)
    print("示例 1: 基础视频分析")
    print("=" * 60)

    from analyzer import BiliAnalyzer

    # 创建分析器
    analyzer = BiliAnalyzer(bv_id="BV1zZcYz1EMy")

    # 获取视频信息
    info = analyzer.get_video_info()
    print(f"\n📺 视频信息:")
    print(f"   标题：{info.get('title', 'N/A')}")
    print(f"   BV 号：{info.get('bvid', 'N/A')}")
    print(f"   时长：{analyzer.format_time(info.get('duration', 0))}")
    print(f"   UP 主：{info.get('owner', {}).get('name', 'N/A')}")

    # 获取统计数据
    stats = analyzer.get_video_stats()
    print(f"\n📊 统计数据:")
    print(f"   播放量：{stats.get('view', 0):,}")
    print(f"   点赞数：{stats.get('like', 0):,}")
    print(f"   弹幕数：{stats.get('danmaku', 0):,}")
    print(f"   收藏数：{stats.get('favorite', 0):,}")


def example_danmaku_analysis():
    """示例 2: 弹幕分析"""
    print("\n" + "=" * 60)
    print("示例 2: 弹幕分析")
    print("=" * 60)

    from analyzer import BiliAnalyzer

    analyzer = BiliAnalyzer(bv_id="BV1zZcYz1EMy")

    # 获取弹幕
    danmaku = analyzer.get_danmaku()
    print(f"\n💬 弹幕总数：{len(danmaku)}")

    # 分析弹幕时间线
    hotspots = analyzer.analyze_danmaku_timeline(danmaku, interval=30)
    print(f"\n🔥 弹幕热点时间段（前 5 个）:")
    for i, spot in enumerate(hotspots[:5], 1):
        time_range = f"{analyzer.format_time(spot['start'])} - {analyzer.format_time(spot['end'])}"
        print(f"   {i}. {time_range}: {spot['count']} 条弹幕")


def example_subtitle_processing():
    """示例 3: 字幕处理"""
    print("\n" + "=" * 60)
    print("示例 3: 字幕处理")
    print("=" * 60)

    from analyzer import BiliAnalyzer
    from subtitle import SubtitleProcessor

    analyzer = BiliAnalyzer(bv_id="BV1zZcYz1EMy")

    # 获取字幕
    subtitles = analyzer.get_subtitles()
    if subtitles:
        print(f"\n📝 找到 {len(subtitles)} 个字幕轨道:")
        for sub in subtitles:
            print(f"   - {sub['language']}: {len(sub['content'])} 条")

        # 使用 SubtitleProcessor 处理字幕
        processor = SubtitleProcessor()
        processor.data = {"body": subtitles[0]["content"]}

        # 提取片段字幕
        clip_subs = processor.extract_clip(start_sec=0, end_sec=30)
        print(f"\n✂️  提取 0-30 秒片段：{len(clip_subs)} 条字幕")

        if clip_subs:
            print("   前 3 条:")
            for item in clip_subs[:3]:
                print(f"   - [{item['from']:.1f}s] {item['content']}")
    else:
        print("\n⚠️  该视频暂无 CC 字幕")


def example_full_analysis():
    """示例 4: 完整分析（一键式）"""
    print("\n" + "=" * 60)
    print("示例 4: 完整分析（一键式）")
    print("=" * 60)

    from analyzer import BiliAnalyzer

    # 注意：实际使用时请替换为有效的 BV 号
    bv_id = "BV1zZcYz1EMy"

    print(f"\n准备分析视频：{bv_id}")
    print("提示：实际使用时请确保 BV 号有效")

    # 完整分析会生成所有文件
    # analyzer = BiliAnalyzer(bv_id)
    # analyzer.analyze(output_dir="./output")

    print("\n✅ 完整分析会生成以下文件:")
    print("   - {BV 号}_full.json       (完整数据)")
    print("   - {BV 号}_danmaku.json    (弹幕数据)")
    print("   - {BV 号}_subtitles.json  (字幕数据)")
    print("   - {BV 号}_timeline.md     (时间轴报告)")


def example_video_clipping():
    """示例 5: 视频切分"""
    print("\n" + "=" * 60)
    print("示例 5: 视频切分")
    print("=" * 60)

    from clipper import VideoClipper

    # 检查 ffmpeg
    clipper = VideoClipper.__new__(VideoClipper)
    has_ffmpeg = clipper.check_ffmpeg()

    if has_ffmpeg:
        print("\n✅ ffmpeg 已安装")

        # 示例切分方案
        print("\n📋 切分方案示例:")
        clips = [
            ("01_opening", 0, 30, "开场片段"),
            ("02_highlight", 60, 30, "亮点片段"),
            ("03_conclusion", 300, 30, "结尾片段"),
        ]

        for name, start, duration, desc in clips:
            print(f"   - {name}: {start}s - {start + duration}s ({desc})")

        # 实际使用示例（需要有效视频文件）
        # clipper = VideoClipper("input.mp4", "output_clips")
        # clipper.add_clips_from_list(clips)
        # clipper.split_all()
    else:
        print("\n⚠️  未检测到 ffmpeg，无法切分视频")
        print("   请安装：brew install ffmpeg (macOS) 或 sudo apt install ffmpeg (Ubuntu)")


def main():
    """运行所有示例"""
    print("\n" + "=" * 60)
    print("bilibili-analyzer 使用示例")
    print("=" * 60)

    # 运行示例
    try:
        example_basic_analyze()
    except Exception as e:
        print(f"\n❌ 示例 1 失败：{e}")

    try:
        example_danmaku_analysis()
    except Exception as e:
        print(f"\n❌ 示例 2 失败：{e}")

    try:
        example_subtitle_processing()
    except Exception as e:
        print(f"\n❌ 示例 3 失败：{e}")

    example_full_analysis()

    example_video_clipping()

    print("\n" + "=" * 60)
    print("所有示例运行完成！")
    print("=" * 60)
    print("\n💡 提示:")
    print("   - 实际使用时请替换为有效的 BV 号")
    print("   - 下载视频需要 Cookie 文件")
    print("   - 视频切分需要安装 ffmpeg")
    print("\n更多用法请查看 README.md")


if __name__ == "__main__":
    main()
