from fastmcp.exceptions import ToolError
from fastmcp.tools import tool
from typing import Annotated
import ffmpeg
import base64
import math

def get_audio_duration(audio_url):
    try:
        print(f"正在远程探测时长: {audio_url}")
        probe = ffmpeg.probe(audio_url)
        duration = float(probe['format']['duration'])
        return duration
    except ffmpeg.Error as e:
        stderr_output = e.stderr.decode('utf-8') if e.stderr else "Unknown error"
        raise ToolError(f"获取时长失败: {stderr_output}")
    except Exception as e:
        raise ToolError(f"探测错误: {e}")

@tool()
def process_remote_audio_chunks(
    audio_url: Annotated[str, "音频地址。"], 
    chunk_duration: Annotated[int, "音频地址切片时长"]) -> str:
    """
    处理音频，每 chunk_duration 秒切一片，转为 MP3 并返回 Base64 列表。
    """
    total_duration = get_audio_duration(audio_url)
    if total_duration <= 0: raise ToolError("音频时长无效")

    num_chunks = math.ceil(total_duration / chunk_duration)
    print(f"音频总时长: {total_duration:.2f} 秒，将分为 {num_chunks} 个片段")

    base64_list = []

    for i in range(num_chunks):
        start_time = i * chunk_duration
        current_duration = min(chunk_duration, total_duration - start_time)
        
        print(f"\n处理片段 [{i+1}/{num_chunks}]: 起始 {start_time:.2f}s, 时长 {current_duration:.2f}s")
        
        try:
            output_data, _ = (
                ffmpeg
                .input(audio_url) 
                .filter('atrim', start=start_time, duration=current_duration)
                .filter('asetpts', 'PTS-STARTPTS')
                .output('pipe:', format='mp3', acodec='libmp3lame')
                .global_args('-loglevel', 'error')
                .run(capture_stdout=True, capture_stderr=True) 
            )
            
            b64_str = base64.b64encode(output_data).decode('utf-8')
            base64_list.append(b64_str)
            print(f"  -> 片段 {i+1} 完成, MP3 大小: {len(output_data) / 1024:.2f} KB")

        except ffmpeg.Error as e:
            stderr_output = e.stderr.decode('utf-8') if e.stderr else "Unknown error"
            raise ToolError(f"FFmpeg 处理片段 {i+1} 失败: {stderr_output}")

    return base64_list
