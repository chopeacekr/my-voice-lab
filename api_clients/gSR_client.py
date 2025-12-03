"""
Google Speech Recognition STT Client
Google STT API를 사용한 음성 인식 클라이언트
"""

import speech_recognition as sr
from pydub import AudioSegment
import io
import tempfile
import os


def preprocess_audio_for_gsr(audio_bytes):
    """
    오디오를 Google STT에 최적화된 형식으로 변환
    
    Args:
        audio_bytes: 원본 오디오 바이트 데이터
    
    Returns:
        str: 전처리된 WAV 파일 경로
    """
    # 임시 파일로 저장
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_input:
        tmp_input.write(audio_bytes)
        tmp_input_path = tmp_input.name
    
    try:
        # pydub으로 오디오 로드
        audio = AudioSegment.from_file(tmp_input_path)
        
        # Google STT 최적 설정
        audio = audio.set_frame_rate(16000)  # 16kHz
        audio = audio.set_channels(1)         # 모노
        
        # 전처리된 파일 저장
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_output:
            tmp_output_path = tmp_output.name
        
        audio.export(tmp_output_path, format="wav")
        
        return tmp_output_path
        
    finally:
        # 입력 임시 파일 삭제
        if os.path.exists(tmp_input_path):
            os.unlink(tmp_input_path)


def google_sr_stt(audio_bytes, lang_code="ko-KR"):
    """
    Google Speech Recognition을 사용한 음성 인식
    
    Args:
        audio_bytes: 오디오 바이트 데이터
        lang_code: 언어 코드 (예: 'ko-KR', 'en-US', 'ja-JP')
    
    Returns:
        str: 인식된 텍스트
    
    Raises:
        RuntimeError: STT 처리 중 오류 발생 시
    """
    processed_file = None
    
    try:
        print(f"🎤 [Google SR] Starting speech recognition...")
        print(f"   - Language: {lang_code}")
        print(f"   - Audio size: {len(audio_bytes)} bytes")
        
        # 1. 오디오 전처리
        print("   🔄 Preprocessing audio...")
        processed_file = preprocess_audio_for_gsr(audio_bytes)
        print(f"   ✅ Audio preprocessed: {processed_file}")
        
        # 2. SpeechRecognition 초기화
        recognizer = sr.Recognizer()
        
        # 3. 오디오 파일 로드
        with sr.AudioFile(processed_file) as source:
            # 주변 소음 조정 (선택)
            print("   🔇 Adjusting for ambient noise...")
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            
            # 오디오 녹음
            print("   🎧 Loading audio...")
            audio_data = recognizer.record(source)
            print(f"   ✅ Audio loaded: {len(audio_data.frame_data)} bytes")
        
        # 4. Google STT 호출
        print("   🌐 Calling Google Speech Recognition API...")
        text = recognizer.recognize_google(audio_data, language=lang_code)
        
        print(f"   ✅ Recognition successful!")
        print(f"   📝 Result: {text}")
        
        return text
        
    except sr.UnknownValueError:
        error_msg = "Google Speech Recognition could not understand audio"
        print(f"   ❌ {error_msg}")
        print("\n   💡 Possible reasons:")
        print("      1. Audio quality too low")
        print("      2. Background noise too loud")
        print("      3. Speech too quiet or unclear")
        print("      4. Wrong language setting")
        print("\n   🔧 Suggestions:")
        print("      - Record in a quiet environment")
        print("      - Speak clearly and loudly")
        print("      - Check language code setting")
        raise RuntimeError(error_msg)
        
    except sr.RequestError as e:
        error_msg = f"Could not request results from Google Speech Recognition: {e}"
        print(f"   ❌ {error_msg}")
        print("\n   💡 Possible reasons:")
        print("      1. No internet connection")
        print("      2. Google API temporarily unavailable")
        print("      3. Rate limit exceeded")
        raise RuntimeError(error_msg)
        
    except Exception as e:
        error_msg = f"Unexpected error during Google SR processing: {e}"
        print(f"   ❌ {error_msg}")
        raise RuntimeError(error_msg)
        
    finally:
        # 전처리된 임시 파일 정리
        if processed_file and os.path.exists(processed_file):
            try:
                os.unlink(processed_file)
                print(f"   🗑️  Cleaned up: {processed_file}")
            except Exception as e:
                print(f"   ⚠️  Failed to clean up {processed_file}: {e}")


def get_supported_languages():
    """
    Google Speech Recognition 지원 언어 목록 반환
    
    Returns:
        dict: 언어 이름 -> 언어 코드 매핑
    """
    return {
        "Korean": "ko-KR",
        "English (US)": "en-US",
        "English (UK)": "en-GB",
        "English (Australia)": "en-AU",
        "English (India)": "en-IN",
        "Japanese": "ja-JP",
        "Chinese (Mandarin)": "zh-CN",
        "Chinese (Cantonese)": "zh-HK",
        "French": "fr-FR",
        "German": "de-DE",
        "Spanish": "es-ES",
        "Italian": "it-IT",
        "Portuguese": "pt-PT",
        "Russian": "ru-RU",
        "Arabic": "ar-SA",
        "Hindi": "hi-IN",
        "Thai": "th-TH",
        "Vietnamese": "vi-VN",
    }


# 테스트 코드
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python gSR_client.py <audio_file.wav> [lang_code]")
        print("\nSupported languages:")
        for lang_name, lang_code in get_supported_languages().items():
            print(f"  {lang_name}: {lang_code}")
        sys.exit(1)
    
    audio_file = sys.argv[1]
    lang_code = sys.argv[2] if len(sys.argv) > 2 else "ko-KR"
    
    # 오디오 파일 읽기
    with open(audio_file, "rb") as f:
        audio_bytes = f.read()
    
    # STT 실행
    try:
        result = google_sr_stt(audio_bytes, lang_code=lang_code)
        print(f"\n✅ Final Result: {result}")
    except RuntimeError as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)