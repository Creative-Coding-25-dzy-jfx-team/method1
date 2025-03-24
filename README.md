# 使用 Quadim 处理视频

此目录包含两个脚本，用于使用 Quadim 对视频进行四叉树风格化处理。您可以选择使用 Python 或 Bash 脚本，两者功能相同。

## 依赖项

- FFmpeg：用于视频处理
- Quadim：用于图像处理 (`cargo install quadim -F build-bin`)
- Python 3.x（如果使用 Python 脚本）
- bc（如果使用 Bash 脚本）

## 安装依赖

1. 安装 FFmpeg：
```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# CentOS/RHEL
sudo dnf install ffmpeg

# macOS
brew install ffmpeg
```

2. 安装 Quadim：
```bash
# 首先确保已安装 Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# 安装 quadim
cargo install quadim -F build-bin
```

3. 安装其他依赖（对于 Bash 脚本）：
```bash
# Ubuntu/Debian
sudo apt install bc

# CentOS/RHEL
sudo dnf install bc

# macOS
brew install bc
```

## 使用方法

### Python 脚本

```bash
./process_video.py <输入视频> [-o 输出视频]

# 示例
./process_video.py input.mp4
./process_video.py input.mp4 -o output.mp4
```

### Bash 脚本

```bash
./process_video.sh <输入视频> [输出视频]

# 示例
./process_video.sh input.mp4
./process_video.sh input.mp4 output.mp4
```

## 参数说明

- `<输入视频>`：要处理的视频文件路径（必需）
- `[输出视频]`：处理后的视频文件路径（可选，默认为 output_video_new.mp4）

## 处理过程

1. 从输入视频中提取所有帧
2. 使用 Quadim 处理每一帧，应用四叉树风格化效果
3. 将处理后的帧重新组合成视频

## 工作目录结构

处理过程中会创建以下目录：
- `frames/`：存放从视频中提取的原始帧
- `output/`：存放 Quadim 处理后的帧

## 注意事项

1. 确保有足够的磁盘空间，因为需要存储视频帧
2. 处理时间取决于视频长度和分辨率
3. 输出视频使用 H.264 编码，应该能在大多数播放器中正常播放

## 脚本特点

- 自动获取视频分辨率并计算合适的比例
- 自动设置合适的缓冲区大小
- 使用通用的视频编码设置确保兼容性
- 包含错误处理和依赖检查
