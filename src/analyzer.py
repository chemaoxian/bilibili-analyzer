#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
B 站视频分析核心模块

功能：
1. 获取视频详细信息
2. 下载视频文件
3. 下载弹幕和字幕
4. 生成时间轴分析
5. 提取关键内容片段
"""

import requests
import re
import json
import os
from datetime import datetime
from typing import Optional, List, Dict, Tuple, Any


class BiliAnalyzer:
    """B 站视频分析器

    用法:
        analyzer = BiliAnalyzer(bv_id="BV1zZcYz1EMy")
        info = analyzer.get_video_info()
        danmaku = analyzer.get_danmaku()
        subtitles = analyzer.get_subtitles()
    """

    # BV 号格式正则：BV 开头 + 10 位 base58 字符（排除 0、O、I、l）
    BV_ID_PATTERN = re.compile(r'^BV1[1-9A-HJ-NP-Za-km-z]{9}$')

    BASE_HEADERS = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://www.bilibili.com",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
    }

    def __init__(self, bv_id: str, cookie_file: Optional[str] = None):
        """初始化分析器

        Args:
            bv_id: B 站视频 BV 号，如 "BV1zZcYz1EMy"
            cookie_file: Cookie 文件路径（用于下载高质量视频）

        Raises:
            ValueError: 当 BV 号格式无效时
        """
        if not self.BV_ID_PATTERN.match(bv_id):
            raise ValueError(
                f"无效的 BV 号格式：{bv_id}。"
                "BV 号格式应为 BV 开头 + 10 位字母数字组合，例如：BV1zZcYz1EMy"
            )
        self.bv_id = bv_id
        self.cookie_file = cookie_file
        self._info_cache: Optional[Dict] = None
        self._stats_cache: Optional[Dict] = None

    def _get_headers(self, with_cookie: bool = False) -> Dict[str, str]:
        """获取请求头"""
        headers = self.BASE_HEADERS.copy()
        if with_cookie and self.cookie_file and os.path.exists(self.cookie_file):
            with open(self.cookie_file, "r", encoding="utf-8") as f:
                headers["Cookie"] = f.read().strip()
        return headers

    def get_video_info(self) -> Dict[str, Any]:
        """获取 B 站视频详细信息"""
        if self._info_cache:
            return self._info_cache

        url = f"https://api.bilibili.com/x/web-interface/view?bvid={self.bv_id}"
        response = requests.get(url, headers=self._get_headers())
        data = response.json()

        if data.get("code") != 0:
            raise Exception(f"获取视频信息失败：{data.get('message', '未知错误')}")

        self._info_cache = data["data"]
        return self._info_cache

    def get_video_stats(self) -> Dict[str, int]:
        """获取视频统计数据"""
        if self._stats_cache:
            return self._stats_cache

        info = self.get_video_info()
        aid = info["aid"]

        # 优先从 info 中获取统计数据
        if info.get("stat"):
            self._stats_cache = {
                "view": info["stat"].get("view", 0),
                "danmaku": info["stat"].get("danmaku", 0),
                "like": info["stat"].get("like", 0),
                "coin": info["stat"].get("coin", 0),
                "favorite": info["stat"].get("favorite", 0),
                "share": info["stat"].get("share", 0),
            }
            return self._stats_cache

        url = f"https://api.bilibili.com/x/web-interface/archive/stat?aid={aid}"
        response = requests.get(url, headers=self._get_headers())
        data = response.json()

        if data.get("code") != 0:
            self._stats_cache = {"view": 0, "danmaku": 0, "like": 0, "coin": 0, "favorite": 0, "share": 0}
        else:
            self._stats_cache = data["data"]

        return self._stats_cache

    def get_danmaku(self) -> List[Dict[str, Any]]:
        """获取视频弹幕"""
        info = self.get_video_info()
        cid = info["pages"][0]["cid"] if info.get("pages") else info["cid"]

        url = f"https://api.bilibili.com/x/v1/dm/list.so?oid={cid}"
        response = requests.get(url, headers=self._get_headers())
        response.encoding = "utf-8"

        danmaku_list = []
        pattern = r'<d p="([^"]*)">([^<]*)</d>'
        matches = re.findall(pattern, response.text)

        for match in matches:
            danmaku_info = match[0].split(",")
            danmaku_list.append({
                "time": float(danmaku_info[0]),
                "type": int(danmaku_info[1]),
                "text": match[1]
            })

        return danmaku_list

    def get_subtitles(self) -> List[Dict[str, Any]]:
        """获取视频字幕（CC 字幕和 AI 字幕）

        注意：AI 字幕需要登录 Cookie 才能获取
        """
        info = self.get_video_info()
        cid = info["pages"][0]["cid"] if info.get("pages") else info["cid"]

        # 使用带 Cookie 的请求头获取字幕（AI 字幕需要登录）
        url = f"https://api.bilibili.com/x/player/v2?cid={cid}&bvid={self.bv_id}"
        response = requests.get(url, headers=self._get_headers(with_cookie=True))
        data = response.json()

        if data.get("code") != 0:
            return []

        subtitles = []
        subtitle_info = data["data"].get("subtitle", {}).get("subtitles", [])

        for sub in subtitle_info:
            lan = sub.get("lan", "")
            # AI 字幕使用 subtitle_url 字段，CC 字幕使用 content_url 字段
            sub_url = sub.get("subtitle_url") or sub.get("content_url", "")
            if sub_url:
                full_url = f"https:{sub_url}" if sub_url.startswith("//") else sub_url
                sub_response = requests.get(full_url, headers=self._get_headers())
                sub_data = sub_response.json()
                subtitles.append({
                    "language": lan,
                    "content": sub_data.get("body", [])
                })

        return subtitles

    def get_play_url(self) -> Tuple[Optional[str], Optional[str]]:
        """获取视频播放地址

        Returns:
            (video_url, audio_url) 或 (None, None)
        """
        info = self.get_video_info()
        aid = info["aid"]
        cid = info["pages"][0]["cid"] if info.get("pages") else info["cid"]

        url = f"https://api.bilibili.com/x/player/playurl?avid={aid}&cid={cid}&qn=80&type=&otype=json&fourk=1&fnver=0&fnval=80"

        response = requests.get(url, headers=self._get_headers(with_cookie=True))
        data = response.json()

        if data.get("code") == 0 and data.get("data"):
            video_data = data["data"]

            # 尝试 dash 格式（高清视频）
            if video_data.get("dash") and video_data["dash"].get("video"):
                video_url = video_data["dash"]["video"][0]["baseUrl"]
                audio_url = video_data["dash"]["audio"][0]["baseUrl"] if video_data["dash"].get("audio") else None
                return video_url, audio_url

            # 尝试 durl 格式（低清视频）
            if video_data.get("durl"):
                return video_data["durl"][0]["url"], None

        return None, None

    def download_file(self, url: str, output_path: str, description: str = "文件") -> bool:
        """下载文件"""
        if not url:
            return False

        print(f"正在下载 {description}...")

        headers = self._get_headers(with_cookie=True)

        try:
            response = requests.get(url, headers=headers, stream=True)
            total_size = int(response.headers.get("content-length", 0))

            with open(output_path, "wb") as f:
                downloaded = 0
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            progress = (downloaded / total_size) * 100
                            print(f"\r下载进度：{progress:.1f}%", end="", flush=True)

            print(f"\n✅ {description}已保存到：{output_path}")
            return True

        except Exception as e:
            print(f"\n❌ {description}下载失败：{e}")
            return False

    def download_video(self, output_path: str) -> bool:
        """下载视频（自动合并音视频）"""
        video_url, audio_url = self.get_play_url()

        if not video_url:
            print("⚠️  无法获取视频播放地址")
            print("   如需下载视频，请创建 Cookie 文件")
            return False

        temp_video = output_path.replace(".mp4", "_video.tmp")
        temp_audio = output_path.replace(".mp4", "_audio.tmp")

        # 下载视频
        self.download_file(video_url, temp_video, "视频")

        # 下载音频（如果有）
        has_audio = False
        if audio_url:
            has_audio = self.download_file(audio_url, temp_audio, "音频")

        # 检查是否有 ffmpeg
        import subprocess
        try:
            subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
            has_ffmpeg = True
        except:
            has_ffmpeg = False

        if has_audio and has_ffmpeg:
            print("\n正在合并音视频...")
            subprocess.run([
                "ffmpeg", "-y",
                "-i", temp_video,
                "-i", temp_audio,
                "-c", "copy",
                output_path
            ], check=True)
            os.remove(temp_video)
            os.remove(temp_audio)
            print(f"✅ 视频已下载并合并：{output_path}")
        elif has_audio:
            print("\n⚠️  未检测到 ffmpeg，无法合并音视频")
            os.rename(temp_video, output_path)
            print(f"✅ 视频已保存到：{output_path}")
        else:
            if os.path.exists(temp_video):
                os.rename(temp_video, output_path)
            print(f"✅ 视频已保存到：{output_path}")

        return True

    @staticmethod
    def analyze_danmaku_timeline(danmaku_list: List[Dict], interval: int = 30) -> List[Dict]:
        """分析弹幕时间线，找出热点片段"""
        if not danmaku_list:
            return []

        timeline = {}
        for dm in danmaku_list:
            bucket = int(dm["time"] // interval) * interval
            if bucket not in timeline:
                timeline[bucket] = []
            timeline[bucket].append(dm["text"])

        hot_spots = []
        for start_time, dms in sorted(timeline.items()):
            hot_spots.append({
                "start": start_time,
                "end": start_time + interval,
                "count": len(dms),
                "keywords": list(set(dms))[:5]
            })

        hot_spots.sort(key=lambda x: x["count"], reverse=True)
        return hot_spots

    @staticmethod
    def generate_clip_suggestions(info: Dict, danmaku_hotspots: List[Dict], subtitles: List[Dict]) -> List[Dict]:
        """生成视频剪辑建议"""
        suggestions = []
        duration = info.get("duration", 0)

        # 推荐开场片段（前 30 秒）
        suggestions.append({
            "type": "opening",
            "start": 0,
            "end": min(30, duration),
            "reason": "视频开场，适合引入主题"
        })

        # 推荐弹幕热点片段
        for spot in danmaku_hotspots[:3]:
            suggestions.append({
                "type": "hotspot",
                "start": spot["start"],
                "end": spot["end"],
                "reason": f"弹幕热点 ({spot['count']} 条)",
                "keywords": spot["keywords"]
            })

        return suggestions

    @staticmethod
    def format_time(seconds: float) -> str:
        """格式化时间为 MM:SS 或 HH:MM:SS"""
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        if h > 0:
            return f"{h}:{m:02d}:{s:02d}"
        return f"{m}:{s:02d}"

    def analyze(self, output_dir: str = ".") -> Dict[str, Any]:
        """综合分析视频，保存所有数据

        Args:
            output_dir: 输出目录

        Returns:
            包含所有分析数据的字典
        """
        os.makedirs(output_dir, exist_ok=True)

        print("=" * 60)
        print("B 站视频分析工具")
        print("=" * 60)

        # 获取基本信息
        print("\n📺 获取视频信息...")
        info = self.get_video_info()
        stats = self.get_video_stats()

        print(f"   标题：{info.get('title', '')}")
        print(f"   时长：{self.format_time(info.get('duration', 0))}")
        print(f"   UP 主：{info.get('owner', {}).get('name', '')}")
        print(f"   播放：{stats.get('view', 0):,}")
        print(f"   点赞：{stats.get('like', 0):,}")

        # 获取弹幕
        print("\n💬 获取弹幕...")
        danmaku = self.get_danmaku()
        print(f"   共 {len(danmaku)} 条")

        # 获取字幕
        print("\n📝 获取字幕...")
        subtitles = self.get_subtitles()
        if subtitles:
            for sub in subtitles:
                print(f"   {sub['language']}: {len(sub['content'])} 条")
        else:
            print("   暂无 CC 字幕")

        # 生成剪辑建议
        print("\n🎬 生成剪辑建议...")
        danmaku_hotspots = self.analyze_danmaku_timeline(danmaku)
        clips = self.generate_clip_suggestions(info, danmaku_hotspots, subtitles)
        print(f"   共 {len(clips)} 个推荐片段")

        # 保存数据
        data = {
            "info": info,
            "stats": stats,
            "danmaku": danmaku,
            "subtitles": subtitles,
            "clips": clips
        }

        # 保存 JSON
        data_path = os.path.join(output_dir, f"{self.bv_id}_full.json")
        with open(data_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"✅ 完整数据已保存到：{data_path}")

        # 保存弹幕
        danmaku_path = os.path.join(output_dir, f"{self.bv_id}_danmaku.json")
        with open(danmaku_path, "w", encoding="utf-8") as f:
            json.dump(danmaku, f, ensure_ascii=False, indent=2)
        print(f"✅ 弹幕已保存到：{danmaku_path}")

        # 保存字幕
        if subtitles:
            sub_path = os.path.join(output_dir, f"{self.bv_id}_subtitles.json")
            with open(sub_path, "w", encoding="utf-8") as f:
                json.dump(subtitles, f, ensure_ascii=False, indent=2)
            print(f"✅ 字幕已保存到：{sub_path}")

        # 保存时间轴报告
        self._save_timeline_report(info, stats, danmaku, subtitles, clips, output_dir)

        print("\n" + "=" * 60)
        print("分析完成！")
        print("=" * 60)

        return data

    def _save_timeline_report(self, info: Dict, stats: Dict, danmaku: List,
                               subtitles: List, clips: List, output_dir: str):
        """保存时间轴分析报告"""
        duration = info.get("duration", 0)
        danmaku_hotspots = self.analyze_danmaku_timeline(danmaku)

        report = f"""# B 站视频时间轴分析报告

## 📺 视频信息

- **标题**: {info.get('title', '')}
- **BV 号**: {info.get('bvid', '')}
- **时长**: {self.format_time(duration)}
- **UP 主**: {info.get('owner', {}).get('name', '')}
- **发布**: {datetime.fromtimestamp(info.get('pubdate', 0)).strftime('%Y-%m-%d')}

---

## 📊 统计数据

| 指标 | 数值 |
|------|------|
| 播放量 | {stats.get('view', 0):,} |
| 点赞数 | {stats.get('like', 0):,} |
| 弹幕数 | {stats.get('danmaku', 0):,} |
| 收藏数 | {stats.get('favorite', 0):,} |

---

## 🎬 推荐剪辑片段

| 类型 | 时间 | 说明 |
|------|------|------|
"""

        for clip in clips:
            time_range = f"{self.format_time(clip['start'])} - {self.format_time(clip['end'])}"
            report += f"| {clip['type']} | {time_range} | {clip['reason']} |\n"

        report += f"""
---

## 🔥 弹幕热点时间轴（每 30 秒）

| 时间段 | 弹幕数 | 关键词 |
|--------|--------|--------|
"""

        for spot in danmaku_hotspots[:10]:
            time_range = f"{self.format_time(spot['start'])} - {self.format_time(spot['end'])}"
            keywords = "; ".join(spot["keywords"][:3])
            report += f"| {time_range} | {spot['count']} | {keywords} |\n"

        report += f"""
---

## 📝 完整字幕时间轴

"""

        if subtitles:
            for sub in subtitles:
                report += f"### {sub['language']}\n\n"
                for item in sub["content"]:
                    report += f"- [{self.format_time(item['from'])}] {item['content']}\n"
        else:
            report += "⚠️ 该视频暂无 CC 字幕\n"

        report += f"""
---

## 💡 PPT 使用建议

1. **视频封面**: 可用于 PPT 配图
2. **数据统计**: 展示 AI 相关内容的热度
3. **弹幕文化**: 展示观众对 AI 工具的态度
4. **剪辑片段**: 可截取关键片段嵌入 PPT

---

*生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

        report_path = os.path.join(output_dir, f"{self.bv_id}_timeline.md")
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report)

        print(f"✅ 时间轴报告已保存到：{report_path}")
