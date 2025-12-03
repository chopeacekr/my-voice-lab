"""
Audio Visualization Utilities
Waveform and Spectrogram 생성
"""

import io
import base64
import zipfile
from pathlib import Path
from datetime import datetime

import numpy as np
import matplotlib
matplotlib.use('Agg')  # GUI 없이 사용
import matplotlib.pyplot as plt
import librosa
import librosa.display
import soundfile as sf


def generate_waveform(audio_bytes, sr=16000, figsize=(10, 3)):
    """
    오디오 Waveform 생성
    
    Args:
        audio_bytes: 오디오 바이트 데이터
        sr: 샘플링 레이트
        figsize: 그래프 크기
    
    Returns:
        bytes: PNG 이미지 바이트
    """
    try:
        # 오디오 데이터 로드
        audio_data, _ = librosa.load(io.BytesIO(audio_bytes), sr=sr)
        
        # Waveform 그래프 생성
        fig, ax = plt.subplots(figsize=figsize)
        librosa.display.waveshow(audio_data, sr=sr, ax=ax, color='#1f77b4')
        
        ax.set_title('Waveform', fontsize=14, fontweight='bold')
        ax.set_xlabel('Time (s)', fontsize=12)
        ax.set_ylabel('Amplitude', fontsize=12)
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # PNG로 저장
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        buf.seek(0)
        image_bytes = buf.read()
        
        plt.close(fig)
        
        return image_bytes
        
    except Exception as e:
        print(f"❌ Waveform 생성 실패: {e}")
        return None


def generate_spectrogram(audio_bytes, sr=16000, figsize=(10, 4)):
    """
    오디오 Spectrogram 생성
    
    Args:
        audio_bytes: 오디오 바이트 데이터
        sr: 샘플링 레이트
        figsize: 그래프 크기
    
    Returns:
        bytes: PNG 이미지 바이트
    """
    try:
        # 오디오 데이터 로드
        audio_data, _ = librosa.load(io.BytesIO(audio_bytes), sr=sr)
        
        # STFT 계산
        D = librosa.stft(audio_data)
        S_db = librosa.amplitude_to_db(np.abs(D), ref=np.max)
        
        # Spectrogram 그래프 생성
        fig, ax = plt.subplots(figsize=figsize)
        img = librosa.display.specshow(
            S_db, 
            sr=sr, 
            x_axis='time', 
            y_axis='hz', 
            ax=ax, 
            cmap='viridis'
        )
        
        ax.set_title('Spectrogram', fontsize=14, fontweight='bold')
        ax.set_xlabel('Time (s)', fontsize=12)
        ax.set_ylabel('Frequency (Hz)', fontsize=12)
        
        fig.colorbar(img, ax=ax, format='%+2.0f dB')
        plt.tight_layout()
        
        # PNG로 저장
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        buf.seek(0)
        image_bytes = buf.read()
        
        plt.close(fig)
        
        return image_bytes
        
    except Exception as e:
        print(f"❌ Spectrogram 생성 실패: {e}")
        return None


def save_audio_with_visualizations(audio_bytes, filename_prefix="audio", sr=16000):
    """
    오디오 파일 + Waveform + Spectrogram을 ZIP으로 압축
    
    Args:
        audio_bytes: 오디오 바이트 데이터
        filename_prefix: 파일명 접두사
        sr: 샘플링 레이트
    
    Returns:
        bytes: ZIP 파일 바이트
        str: ZIP 파일명
    """
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_filename = f"{filename_prefix}_{timestamp}.zip"
        
        # ZIP 파일 생성
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # 1. 원본 오디오 파일
            audio_filename = f"{filename_prefix}_{timestamp}.wav"
            zipf.writestr(audio_filename, audio_bytes)
            print(f"   ✅ Added: {audio_filename}")
            
            # 2. Waveform 이미지
            waveform_bytes = generate_waveform(audio_bytes, sr=sr)
            if waveform_bytes:
                waveform_filename = f"{filename_prefix}_{timestamp}_waveform.png"
                zipf.writestr(waveform_filename, waveform_bytes)
                print(f"   ✅ Added: {waveform_filename}")
            
            # 3. Spectrogram 이미지
            spectrogram_bytes = generate_spectrogram(audio_bytes, sr=sr)
            if spectrogram_bytes:
                spectrogram_filename = f"{filename_prefix}_{timestamp}_spectrogram.png"
                zipf.writestr(spectrogram_filename, spectrogram_bytes)
                print(f"   ✅ Added: {spectrogram_filename}")
        
        zip_buffer.seek(0)
        zip_bytes = zip_buffer.read()
        
        print(f"   📦 ZIP created: {len(zip_bytes)} bytes")
        
        return zip_bytes, zip_filename
        
    except Exception as e:
        print(f"❌ ZIP 생성 실패: {e}")
        return None, None


def audio_bytes_to_base64_image(image_bytes):
    """
    이미지 바이트를 Base64 인코딩된 HTML img 태그로 변환
    
    Args:
        image_bytes: PNG 이미지 바이트
    
    Returns:
        str: HTML img 태그
    """
    if image_bytes is None:
        return ""
    
    image_b64 = base64.b64encode(image_bytes).decode('utf-8')
    return f'<img src="data:image/png;base64,{image_b64}" style="width:100%; max-width:800px;">'


# 테스트 코드
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python audio_visualizer.py <audio_file.wav>")
        sys.exit(1)
    
    audio_file = sys.argv[1]
    
    # 오디오 파일 읽기
    with open(audio_file, "rb") as f:
        audio_bytes = f.read()
    
    print(f"📊 Audio file: {audio_file}")
    print(f"📊 Size: {len(audio_bytes)} bytes")
    
    # Waveform 생성
    print("\n🎨 Generating waveform...")
    waveform_bytes = generate_waveform(audio_bytes)
    if waveform_bytes:
        with open("test_waveform.png", "wb") as f:
            f.write(waveform_bytes)
        print("✅ Waveform saved: test_waveform.png")
    
    # Spectrogram 생성
    print("\n🎨 Generating spectrogram...")
    spectrogram_bytes = generate_spectrogram(audio_bytes)
    if spectrogram_bytes:
        with open("test_spectrogram.png", "wb") as f:
            f.write(spectrogram_bytes)
        print("✅ Spectrogram saved: test_spectrogram.png")
    
    # ZIP 생성
    print("\n📦 Creating ZIP...")
    zip_bytes, zip_filename = save_audio_with_visualizations(audio_bytes, "test")
    if zip_bytes:
        with open(zip_filename, "wb") as f:
            f.write(zip_bytes)
        print(f"✅ ZIP saved: {zip_filename}")
    
    print("\n🎉 Done!")