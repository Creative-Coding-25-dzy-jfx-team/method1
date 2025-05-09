#!/usr/bin/env python3
"""
使用 quadim 处理视频的 Python 脚本.
此脚本将：
1. 将输入视频拆分为帧
2. 使用 quadim 处理每一帧
3. 将处理后的帧重新组合成视频

依赖:
- FFmpeg
- quadim (cargo install quadim -F build-bin)
- Python 3.x
"""

import os
import subprocess
import argparse
from pathlib import Path

def create_directories(base_dir):
    """创建用于存放帧的目录"""
    frames_dir = os.path.join(base_dir, "frames")
    output_dir = os.path.join(base_dir, "output")
    
    for dir_path in [frames_dir, output_dir]:
        os.makedirs(dir_path, exist_ok=True)
    
    return frames_dir, output_dir

def extract_video_info(video_path):
    """获取视频信息（分辨率、帧率等）"""
    cmd = ["ffmpeg", "-i", video_path]
    try:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        _, output = process.communicate()
    except subprocess.CalledProcessError as e:
        output = e.stderr
    
    print("Raw FFmpeg output:")
    print(output)
    print("--- End of FFmpeg output ---")

    # 解析视频信息
    for line in output.split('\n'):
        if "Stream #" in line and "Video:" in line:
            # Match resolution in video stream line format
            import re
            match = re.search(r'Stream.*Video:.*?, (\d+)x(\d+)', line)
            if match:
                width, height = map(int, match.groups())
                if width == 0 or height == 0:
                    return None
                ratio = f"{round(width/height*10)}:10" if width > height else f"10:{round(height/width*10)}"
                return {
                    'width': width,
                    'height': height,
                    'ratio': ratio,
                    'buffer_size': width * height * 4  # Multiply by 4 for RGBA buffer
                }
    return None

def extract_frames(video_path, frames_dir):
    """将视频拆分为帧"""
    cmd = [
        "ffmpeg",
        "-i", video_path,
        "-q", "2",
        os.path.join(frames_dir, "%05d.jpg")
    ]
    subprocess.run(cmd, check=True)

def process_frames(frames_dir, output_dir, video_info):
    """使用 quadim 处理帧"""
    cmd = [
        "quadim",
        frames_dir,
        "-o", output_dir,
        "--ratio", video_info['ratio'],
        "--depth", "8",
        "--stroke-width", "1",
        "--fps", "30",
        "--buffer", str(video_info['buffer_size'])
    ]
    subprocess.run(cmd, check=True)

def combine_frames(output_dir, final_output, video_info):
    """将处理后的帧合并为视频"""
    cmd = [
        "ffmpeg",
        "-framerate", "30",
        "-i", os.path.join(output_dir, "%05d.png"),
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-preset", "medium",
        "-crf", "20",
        final_output
    ]
    subprocess.run(cmd, check=True)

def main():
    parser = argparse.ArgumentParser(description="使用 quadim 处理视频")
    parser.add_argument("video_path", help="输入视频文件的路径")
    parser.add_argument("-o", "--output", help="输出视频文件的路径", default="output_video_new.mp4")
    args = parser.parse_args()

    # 确保视频文件存在
    if not os.path.exists(args.video_path):
        print(f"错误：找不到视频文件 {args.video_path}")
        return

    # 创建工作目录
    base_dir = os.path.dirname(os.path.abspath(args.video_path))
    frames_dir, output_dir = create_directories(base_dir)

    # 获取视频信息
    print("正在分析视频...")
    video_info = extract_video_info(args.video_path)
    if not video_info:
        print("错误：无法获取视频信息")
        return

    try:
        # 处理视频
        print("正在提取帧...")
        extract_frames(args.video_path, frames_dir)

        print("正在使用 quadim 处理帧...")
        process_frames(frames_dir, output_dir, video_info)

        print("正在合成视频...")
        final_output = os.path.join(base_dir, args.output)
        combine_frames(output_dir, final_output, video_info)

        print(f"处理完成！输出文件：{final_output}")

    except subprocess.CalledProcessError as e:
        print(f"错误：处理过程中出现问题：{e}")
    except Exception as e:
        print(f"错误：{e}")

if __name__ == "__main__":
    main()
