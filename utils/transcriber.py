import os
from itertools import groupby

from faster_whisper import WhisperModel
from pyannote.audio import Pipeline
from pydub import AudioSegment
import tempfile
import torch
import torchaudio
import wave
import contextlib
from huggingface_hub import login

# 读取 HuggingFace token（从环境变量中）
token = os.getenv("HUGGINGFACE_TOKEN")
if not token:
    raise EnvironmentError("❌ 请先设置环境变量 HUGGINGFACE_TOKEN")
else:
    print("🔐 HuggingFace token loaded.")

# 登录 HuggingFace
login(token)

# 初始化 Whisper 模型（本地语音转文字）
model = WhisperModel("small", compute_type="int8")

# 初始化 PyAnnote 说话人分离模型
diarization_pipeline = Pipeline.from_pretrained(
    "pyannote/speaker-diarization",
    use_auth_token=token
)

# 获取音频时长
def get_audio_duration(filepath):
    try:
        # 自动根据格式读取音频（支持mp3、wav、flac、m4a等）
        audio = AudioSegment.from_file(filepath)
        duration = len(audio) / 1000.0  # 转换为秒
        return duration
    except Exception as e:
        print("❌ 无法读取音频时长：", e)
        return 0

# 将任何格式的音频统一转成 wav 临时文件
def convert_to_wav(filepath):
    if filepath.endswith(".wav"):
        return filepath  # 已是 wav，不处理

    try:
        audio = AudioSegment.from_file(filepath)
        new_path = filepath.rsplit(".", 1)[0] + ".wav"
        audio.export(new_path, format="wav")
        return new_path
    except Exception as e:
        print(f"[错误] 音频转换失败: {e}")
        return None




# 执行说话人分离 + 语音识别
def transcribe_with_speakers(filepath):
    try:
        filepath = convert_to_wav(filepath)
        if not filepath:
            print("❌ 音频格式转换失败")
            return None

        # 获取音频时长
        duration = get_audio_duration(filepath)
        if duration < 1:
            print("❌ 音频过短或无效")
            return None

        # 执行说话人分离
        diarization = diarization_pipeline(filepath)
        print("✅ 完成说话人分离")

        # 将说话人分离结果整理为 [(start, end, speaker)] 列表
        speaker_segments = []
        for turn in diarization.itertracks(yield_label=True):
            start = turn[0].start
            end = turn[0].end
            speaker = turn[2]
            speaker_segments.append((start, end, speaker))

        # 执行语音识别
        segments, _ = model.transcribe(filepath, beam_size=5, language="zh")
        print("✅ 完成语音识别")

        # 将识别结果映射到对应的说话人
        dialogue = []
        for segment in segments:
            segment_start = segment.start
            segment_end = segment.end
            text = segment.text.strip()
            # 默认未识别到说话人
            speaker_label = speaker if speaker else "SPEAKER"
            # 在说话人列表中查找当前识别片段属于哪个人说的
            for start, end, speaker in speaker_segments:
                # 如果时间段有交集（允许一定重叠）
                if start <= segment_start <= end or start <= segment_end <= end:
                    speaker_label = speaker
                    break
            dialogue.append((speaker_label, text))

        if not dialogue:
            print("⚠ 没有任何识别文本")
            return None

        # 按照说话人连续说的内容进行分段组合
        grouped = []
        for speaker, lines in groupby(dialogue, key=lambda x: x[0]):
            lines_text = " ".join(line for _, line in lines)
            grouped.append(f"{speaker}：{lines_text}")

        result_text =  "\n\n".join(grouped)
        print("✅ 语音转写输出：", result_text)
        return result_text

    except Exception as e:
        print(f"[错误] 转写失败：{e}")
        return None

