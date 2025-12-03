"""
Audio Processing Utilities
오디오 전처리 및 변환
"""

import io
from pydub import AudioSegment


def preprocess_audio_for_stt(audio_segment: AudioSegment, target_sample_rate: int = 16000) -> bytes:
    """
    STT를 위한 오디오 전처리
    
    Args:
        audio_segment: Pydub AudioSegment 객체
        target_sample_rate: 목표 샘플링 레이트 (기본: 16000Hz)
    
    Returns:
        bytes: 전처리된 WAV 바이트 데이터
    """
    # 모노로 변환 (스테레오 → 모노)
    if audio_segment.channels > 1:
        audio_segment = audio_segment.set_channels(1)
        print(f"   🔄 Channels: Stereo → Mono")
    
    # 샘플링 레이트 변환
    if audio_segment.frame_rate != target_sample_rate:
        print(f"   🔄 Sample rate: {audio_segment.frame_rate}Hz → {target_sample_rate}Hz")
        audio_segment = audio_segment.set_frame_rate(target_sample_rate)
    
    # WAV 형식으로 내보내기
    buffer = io.BytesIO()
    audio_segment.export(buffer, format="wav")
    buffer.seek(0)
    
    return buffer.getvalue()


def audio_segment_to_bytes(audio_segment: AudioSegment, format="wav") -> bytes:
    """
    AudioSegment를 바이트로 변환
    
    Args:
        audio_segment: Pydub AudioSegment 객체
        format: 출력 포맷 (wav, mp3 등)
    
    Returns:
        bytes: 오디오 바이트 데이터
    """
    buffer = io.BytesIO()
    audio_segment.export(buffer, format=format)
    buffer.seek(0)
    return buffer.getvalue()


def bytes_to_audio_segment(audio_bytes: bytes) -> AudioSegment:
    """
    바이트를 AudioSegment로 변환
    
    Args:
        audio_bytes: 오디오 바이트 데이터
    
    Returns:
        AudioSegment: Pydub AudioSegment 객체
    """
    return AudioSegment.from_file(io.BytesIO(audio_bytes))


# 테스트 코드
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python audio_processor.py <audio_file>")
        sys.exit(1)
    
    audio_file = sys.argv[1]
    
    # 오디오 파일 읽기
    audio = AudioSegment.from_file(audio_file)
    
    print(f"📊 Original Audio:")
    print(f"   - Channels: {audio.channels}")
    print(f"   - Sample rate: {audio.frame_rate}Hz")
    print(f"   - Duration: {len(audio)/1000:.2f}s")
    
    # 전처리
    print(f"\n🔄 Preprocessing...")
    audio_bytes = preprocess_audio_for_stt(audio, target_sample_rate=16000)
    
    # 전처리 결과
    processed_audio = bytes_to_audio_segment(audio_bytes)
    print(f"\n📊 Processed Audio:")
    print(f"   - Channels: {processed_audio.channels}")
    print(f"   - Sample rate: {processed_audio.frame_rate}Hz")
    print(f"   - Size: {len(audio_bytes)} bytes")
    
    print(f"\n✅ Done!")