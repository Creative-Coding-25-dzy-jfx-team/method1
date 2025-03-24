#!/bin/bash

# 使用 quadim 处理视频的 Bash 脚本
# 依赖:
# - FFmpeg
# - quadim (cargo install quadim -F build-bin)
# - bc (用于计算)

# 显示使用方法
show_usage() {
    echo "使用方法: $0 <输入视频> [输出视频]"
    echo
    echo "参数:"
    echo "  输入视频    要处理的视频文件路径"
    echo "  输出视频    处理后的视频文件路径 (可选，默认: output_video_new.mp4)"
    echo
    echo "示例:"
    echo "  $0 input.mp4"
    echo "  $0 input.mp4 output.mp4"
    exit 1
}

# 检查依赖
check_dependencies() {
    local missing_deps=()
    
    # 检查 FFmpeg
    if ! command -v ffmpeg &> /dev/null; then
        missing_deps+=("FFmpeg")
    fi
    
    # 检查 quadim
    if ! command -v quadim &> /dev/null; then
        missing_deps+=("quadim")
    fi
    
    # 检查 bc
    if ! command -v bc &> /dev/null; then
        missing_deps+=("bc")
    fi
    
    # 如果有缺失的依赖，显示提示并退出
    if [ ${#missing_deps[@]} -ne 0 ]; then
        echo "错误：以下依赖未安装："
        for dep in "${missing_deps[@]}"; do
            echo "- $dep"
        done
        echo
        echo "请安装缺失的依赖后重试。"
        echo "quadim 可以通过以下命令安装："
        echo "cargo install quadim -F build-bin"
        exit 1
    fi
}

# 获取视频信息
get_video_info() {
    local video_path="$1"
    local info
    
    # 使用 FFmpeg 获取视频信息
    info=$(ffmpeg -i "$video_path" 2>&1)
    
    # 获取视频分辨率
    local resolution=$(echo "$info" | grep -oP "\d+x\d+" | head -n1)
    if [ -z "$resolution" ]; then
        echo "错误：无法获取视频分辨率"
        exit 1
    fi
    
    # 分离宽度和高度
    width=$(echo "$resolution" | cut -d'x' -f1)
    height=$(echo "$resolution" | cut -d'x' -f2)
    
    # 计算比例（乘以10并四舍五入）
    ratio=$(echo "scale=0; ($width/$height*10)/1" | bc)
    
    # 输出信息
    echo "width=$width"
    echo "height=$height"
    echo "ratio=${ratio}:10"
    echo "buffer_size=$((width * height))"
}

# 主处理函数
process_video() {
    local input_video="$1"
    local output_video="${2:-output_video_new.mp4}"
    local base_dir=$(dirname "$(realpath "$input_video")")
    local frames_dir="$base_dir/frames"
    local output_dir="$base_dir/output"
    
    # 创建必要的目录
    mkdir -p "$frames_dir" "$output_dir"
    
    echo "正在分析视频..."
    # 获取视频信息
    eval "$(get_video_info "$input_video")"
    
    echo "正在提取帧..."
    ffmpeg -i "$input_video" -q 2 "$frames_dir/%05d.jpg"
    
    echo "正在使用 quadim 处理帧..."
    quadim "$frames_dir" \
        -o "$output_dir" \
        --ratio "${ratio}:10" \
        --depth 8 \
        --stroke-width 1 \
        --fps 30 \
        --buffer "$buffer_size"
    
    echo "正在合成视频..."
    ffmpeg -framerate 30 \
        -i "$output_dir/%05d.png" \
        -c:v libx264 \
        -pix_fmt yuv420p \
        -preset medium \
        -crf 20 \
        "$output_video"
    
    echo "处理完成！输出文件：$output_video"
}

# 主程序
main() {
    # 检查参数
    if [ $# -lt 1 ]; then
        show_usage
    fi
    
    # 检查输入文件是否存在
    if [ ! -f "$1" ]; then
        echo "错误：输入文件 '$1' 不存在"
        exit 1
    fi
    
    # 检查依赖
    check_dependencies
    
    # 处理视频
    process_video "$@"
}

# 运行主程序
main "$@"
