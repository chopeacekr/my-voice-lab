"""
Bark TTS Client for my-voice-lab

Bark TTS 서버와 통신하는 클라이언트 모듈
"""

import requests
import base64
from typing import Optional


def check_bark_health() -> dict:
    """
    Bark TTS 서버 헬스 체크
    
    Returns:
        dict: 서버 상태 정보
    """
    try:
        response = requests.get("http://localhost:8600/health", timeout=2)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"status": "error", "message": str(e)}


def bark_tts_http(
    text: str,
    voice_preset: Optional[str] = None,
    speed: float = 1.0,
) -> str:
    """
    Bark TTS를 사용하여 텍스트를 음성으로 변환
    
    Args:
        text: 변환할 텍스트
            - 특수 토큰 사용 가능: [laughs], [sighs], [cries], [music]
        voice_preset: 화자 프리셋 (예: v2/en_speaker_0, v2/ko_speaker_1)
            - None이면 기본 화자 사용
        speed: 음성 속도 (0.5 ~ 2.0)
    
    Returns:
        str: HTML audio 태그 (base64 인코딩된 오디오)
    
    Example:
        >>> # 기본 사용
        >>> audio_html = bark_tts_http("안녕하세요!")
        
        >>> # 감정 표현
        >>> audio_html = bark_tts_http("오늘 너무 기쁩니다! [laughs]")
        
        >>> # 화자 지정
        >>> audio_html = bark_tts_http(
        ...     "Hello, how are you?",
        ...     voice_preset="v2/en_speaker_0"
        ... )
        
        >>> # 속도 조절
        >>> audio_html = bark_tts_http("빠르게 말합니다", speed=1.5)
    """
    try:
        # 요청 데이터 준비 (Form 형식)
        files = {
            "text": (None, text),
            "speed": (None, str(speed)),
        }
        
        if voice_preset:
            files["voice_preset"] = (None, voice_preset)
        
        # Bark TTS 서버에 POST 요청
        response = requests.post(
            "http://localhost:8600/synthesize",
            files=files,
            timeout=500  # Bark는 처리 시간이 매우 길 수 있음 (5분)
        )
        response.raise_for_status()
        
        # 오디오 바이트 받기
        audio_bytes = response.content
        
        # Base64 인코딩
        b64_audio = base64.b64encode(audio_bytes).decode("utf-8")
        
        # HTML audio 태그 생성
        audio_html = f'<audio controls><source src="data:audio/wav;base64,{b64_audio}" type="audio/wav"></audio>'
        
        return audio_html
        
    except requests.exceptions.RequestException as e:
        error_message = f"Bark TTS 요청 실패: {str(e)}"
        print(error_message)
        return f'<p style="color: red;">{error_message}</p>'
    except Exception as e:
        error_message = f"예상치 못한 오류: {str(e)}"
        print(error_message)
        return f'<p style="color: red;">{error_message}</p>'


# 화자 프리셋 목록 (참고용)
BARK_VOICE_PRESETS = {
    "english": [
        "v2/en_speaker_0", "v2/en_speaker_1", "v2/en_speaker_2",
        "v2/en_speaker_3", "v2/en_speaker_4", "v2/en_speaker_5",
        "v2/en_speaker_6", "v2/en_speaker_7", "v2/en_speaker_8",
        "v2/en_speaker_9",
    ],
    "korean": [
        "v2/ko_speaker_0", "v2/ko_speaker_1", "v2/ko_speaker_2",
        "v2/ko_speaker_3", "v2/ko_speaker_4", "v2/ko_speaker_5",
    ],
    "chinese": [
        "v2/zh_speaker_0", "v2/zh_speaker_1", "v2/zh_speaker_2",
        "v2/zh_speaker_3", "v2/zh_speaker_4",
    ],
}

# 특수 토큰 사용 예시
BARK_SPECIAL_TOKENS = {
    "emotions": {
        "laughs": "[laughs]",
        "sighs": "[sighs]",
        "cries": "[cries]",
        "gasps": "[gasps]",
    },
    "sounds": {
        "music": "[music]",
        "applause": "[applause]",
    }
}


if __name__ == "__main__":
    # 테스트 코드
    print("Bark TTS Client 테스트")
    print("=" * 50)
    
    # 헬스 체크
    print("\n1. 헬스 체크:")
    health = check_bark_health()
    print(f"   상태: {health}")
    
    # 기본 TTS
    print("\n2. 기본 TTS 테스트:")
    result = bark_tts_http("안녕하세요, Bark TTS 테스트입니다.")
    print(f"   결과: {result[:100]}...")
    
    # 감정 표현
    print("\n3. 감정 표현 테스트:")
    result = bark_tts_http("정말 기쁩니다! [laughs]")
    print(f"   결과: {result[:100]}...")
    
    print("\n테스트 완료!")