# api_clients/vosk_client.py

import os
import base64
import requests

# Vosk 서버 URL (환경변수로 오버라이드 가능)
VOSK_SERVER_URL = os.environ.get("VOSK_SERVER_URL", "http://127.0.0.1:8200")


def _build_url(path: str) -> str:
    """헬스체크, transcribe 등 엔드포인트 URL 생성"""
    return f"{VOSK_SERVER_URL.rstrip('/')}{path}"


def check_vosk_health() -> dict:
    """
    Vosk 서버 상태 확인용.
    - 정상: {"status": "ok", "loaded_languages": [...], "supported_languages": [...]}
    - 실패: {"status": "error", "detail": "..."}
    """
    try:
        resp = requests.get(_build_url("/health"), timeout=5)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return {
            "status": "error",
            "detail": str(e),
        }


def vosk_stt_http(
    audio_bytes: bytes,
    lang: str = "KR",
    sample_rate: int = 16000,
) -> str:
    """
    Vosk STT 서버(/transcribe)에 WAV 바이트를 보내서 텍스트를 받아온다.

    Parameters
    ----------
    audio_bytes : bytes
        WAV 형식의 오디오 데이터
    lang : str
        서버에서 사용하는 언어 코드 ("KR", "EN", "JP", "ZH", ...)
    sample_rate : int
        클라이언트 쪽에서 인지하고 있는 샘플레이트 (기본 16000)

    Returns
    -------
    str
        인식된 텍스트 (빈 문자열 가능)

    Raises
    ------
    RuntimeError
        서버 요청 실패 또는 응답 포맷 오류 시
    """
    # 1) 오디오를 base64로 인코딩
    audio_b64 = base64.b64encode(audio_bytes).decode("ascii")

    payload = {
        "audio_base64": audio_b64,
        "lang": lang,
        "sample_rate": sample_rate,
    }

    try:
        resp = requests.post(
            _build_url("/transcribe"),
            json=payload,
            timeout=60,
        )
        resp.raise_for_status()
    except Exception as e:
        raise RuntimeError(f"Vosk STT server request failed: {e}") from e

    try:
        data = resp.json()
    except Exception as e:
        raise RuntimeError(f"Invalid JSON response from Vosk STT server: {e}") from e

    text = data.get("text", "")
    if not isinstance(text, str):
        raise RuntimeError(f"Unexpected response format from Vosk STT server: {data}")

    return text.strip()
