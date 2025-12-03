"""
Wav2Vec2 STT Client
my-voice-lab에서 Wav2Vec2 STT 서버와 통신하는 클라이언트

서버: http://localhost:8400
"""

import io
import base64
import requests
from typing import Optional


# Wav2Vec2 서버 설정
WAV2VEC2_SERVER_URL = "http://localhost:8400"


def check_wav2vec2_health() -> dict:
    """
    Wav2Vec2 STT 서버 헬스 체크
    
    Returns:
        dict: {
            "status": "ok" | "error",
            "model_loaded": bool,
            "processor_loaded": bool,
            "device": "cpu" | "cuda",
            "model_id": str
        }
    
    Raises:
        Exception: 서버 연결 실패 시
    """
    try:
        response = requests.get(f"{WAV2VEC2_SERVER_URL}/health", timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise Exception(f"Wav2Vec2 서버 연결 실패: {e}")


def wav2vec2_stt_http(
    audio_bytes: bytes,
    lang: str = "KR",
    sample_rate: int = 16000
) -> str:
    """
    Wav2Vec2 STT 서버로 오디오 전송 및 텍스트 변환
    
    Args:
        audio_bytes: WAV 오디오 바이트 (16kHz, 모노 권장)
        lang: 언어 코드 (기본: KR)
        sample_rate: 샘플레이트 (기본: 16000)
    
    Returns:
        str: 변환된 텍스트
    
    Raises:
        RuntimeError: 서버 오류 또는 변환 실패 시
    
    Example:
        >>> with open("audio.wav", "rb") as f:
        ...     audio_bytes = f.read()
        >>> text = wav2vec2_stt_http(audio_bytes, lang="KR")
        >>> print(text)
        "안녕하세요"
    """
    try:
        print(f"\n🎤 [Wav2Vec2 STT] 요청 시작")
        print(f"   - 오디오 크기: {len(audio_bytes)} bytes")
        print(f"   - 언어: {lang}")
        print(f"   - 샘플레이트: {sample_rate}Hz")
        
        # 파일 형식으로 전송
        files = {
            "file": ("audio.wav", io.BytesIO(audio_bytes), "audio/wav")
        }
        data = {
            "lang": lang
        }
        
        # POST 요청
        response = requests.post(
            f"{WAV2VEC2_SERVER_URL}/transcribe",
            files=files,
            data=data,
            timeout=90  # 30초 타임아웃
        )
        
        # HTTP 에러 체크
        if response.status_code != 200:
            error_detail = response.json().get("detail", "알 수 없는 오류")
            raise RuntimeError(
                f"Wav2Vec2 서버 오류 (HTTP {response.status_code}): {error_detail}"
            )
        
        # 응답 파싱
        result = response.json()
        text = result.get("text", "").strip()
        
        print(f"✅ [Wav2Vec2 STT] 변환 완료: '{text}'")
        
        if not text:
            print("⚠️  [Wav2Vec2 STT] 경고: 빈 텍스트 반환")
        
        return text
        
    except requests.Timeout:
        raise RuntimeError(
            "Wav2Vec2 서버 응답 시간 초과 (30초). "
            "오디오가 너무 길거나 서버가 과부하 상태일 수 있습니다."
        )
    except requests.ConnectionError:
        raise RuntimeError(
            "Wav2Vec2 서버에 연결할 수 없습니다. "
            "서버가 실행 중인지 확인하세요 (포트: 8400)"
        )
    except Exception as e:
        raise RuntimeError(f"Wav2Vec2 STT 처리 실패: {e}")


def wav2vec2_stt_test():
    """
    Wav2Vec2 STT 클라이언트 테스트
    
    실제 오디오 파일로 테스트하려면:
    python -c "from api_clients.wav2vec2_client import wav2vec2_stt_test; wav2vec2_stt_test()"
    """
    print("\n" + "="*60)
    print("Wav2Vec2 STT Client 테스트")
    print("="*60)
    
    # 1. 헬스 체크
    print("\n1️⃣ 서버 헬스 체크")
    try:
        health = check_wav2vec2_health()
        print(f"   ✅ 상태: {health.get('status')}")
        print(f"   📦 모델: {health.get('model_id')}")
        print(f"   💻 디바이스: {health.get('device')}")
    except Exception as e:
        print(f"   ❌ 실패: {e}")
        return
    
    # 2. 테스트 오디오 파일 확인
    print("\n2️⃣ 테스트 오디오 파일 확인")
    import os
    
    test_files = [
        "test_audio.wav",
        "my_voice1.wav",
        "../test_audio.wav",
    ]
    
    test_file = None
    for f in test_files:
        if os.path.exists(f):
            test_file = f
            break
    
    if not test_file:
        print("   ⚠️  테스트 오디오 파일을 찾을 수 없습니다.")
        print("   💡 'test_audio.wav' 파일을 현재 디렉토리에 추가하세요.")
        return
    
    print(f"   ✅ 파일 발견: {test_file}")
    
    # 3. STT 테스트
    print("\n3️⃣ STT 변환 테스트")
    try:
        with open(test_file, "rb") as f:
            audio_bytes = f.read()
        
        text = wav2vec2_stt_http(audio_bytes, lang="KR")
        
        print(f"\n   🎉 변환 성공!")
        print(f"   📝 결과: '{text}'")
        
    except Exception as e:
        print(f"   ❌ 실패: {e}")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    # 테스트 실행
    wav2vec2_stt_test()