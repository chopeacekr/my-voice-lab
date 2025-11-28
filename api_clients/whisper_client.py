"""
Whisper STT Client
HTTP client for Whisper STT server
"""

import base64
import requests

# Whisper STT 서버 URL
WHISPER_SERVER_URL = "http://127.0.0.1:8300" ##"http://localhost:8300"

def whisper_stt_http(audio_bytes, lang="KR", sample_rate=16000, timeout=60):
    """
    Whisper STT 서버를 통해 음성을 텍스트로 변환
    
    Args:
        audio_bytes: WAV 오디오 데이터 (bytes)
        lang: 언어 코드 ("KR", "EN", "JP", "ZH", "FR", "DE", "ES", "RU")
        sample_rate: 샘플링 레이트 (기본 16000)
        timeout: 타임아웃 (초)
    
    Returns:
        str: 인식된 텍스트
    """
    try:
        audio_b64 = base64.b64encode(audio_bytes).decode('utf-8')
        payload = {"audio_b64": audio_b64, "lang": lang, "sample_rate": sample_rate}
        response = requests.post(f"{WHISPER_SERVER_URL}/recognize", json=payload, timeout=timeout)
        response.raise_for_status()
        return response.json().get("text", "")
    except requests.exceptions.Timeout:
        raise ValueError(f"Whisper STT server timeout (>{timeout}s). Server might be slow or not responding.")
    except requests.exceptions.ConnectionError:
        raise ValueError(f"Cannot connect to Whisper STT server at {WHISPER_SERVER_URL}. Is the server running?")
    except Exception as e:
        raise ValueError(f"Whisper STT request failed: {e}")


def check_whisper_health():
    """
    Whisper STT 서버 상태 확인
    
    Returns:
        dict: 서버 상태 정보
    """
    try:
        response = requests.get(f"{WHISPER_SERVER_URL}/health", timeout=5)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"status": "error", "message": f"Cannot connect to server: {e}"}