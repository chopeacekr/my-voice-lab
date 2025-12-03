# melotts_client.py

import os
import base64
import requests


# MeloTTS 서버 URL (환경변수로 오버라이드 가능)
MELOTTS_SERVER_URL = os.environ.get("MELOTTS_SERVER_URL", "http://127.0.0.1:8000")


def embed_audio_from_base64(b64: str, mime_type: str = "audio/wav") -> str:
    """
    base64 인코딩된 오디오 데이터를 <audio> 태그로 감싼 HTML 문자열로 변환.
    web.py에서 그대로 사용하기 위해 기존 형식을 유지.
    """
    html = f"""<audio controls>
    <source src="data:{mime_type};base64,{b64}" type="{mime_type}">
    Your browser does not support the audio element.
</audio>"""
    return html


def melotts_tts_http(
    text: str,
    melo_lang_code: str,
    speed: float = 1.0,
    speaker: str | None = None,
    base_url: str | None = None,
) -> str:
    """
    MeloTTS 서버의 /synthesize_base64 엔드포인트를 호출해서
    base64 오디오를 받아온 뒤, <audio> HTML을 리턴.

    - text: 합성할 텍스트
    - melo_lang_code: "KR", "EN", "JP", "ZH" 등 MeloTTS 언어 코드
    - speed: 말하기 속도
    - speaker: 화자 이름(옵션, 보통 None)
    - base_url: 기본은 환경변수 MELOTTS_SERVER_URL 또는 "http://127.0.0.1:8000"
    """
    url_base = base_url or MELOTTS_SERVER_URL
    url = f"{url_base.rstrip('/')}/synthesize_base64"

    payload = {
        "text": text,
        "lang": melo_lang_code,
        "speaker": speaker,
        "speed": speed,
    }

    try:
        resp = requests.post(url, json=payload, timeout=180)
        resp.raise_for_status()
    except Exception as e:
        # web.py에서 바로 표시하기 쉽게 RuntimeError로 래핑
        raise RuntimeError(f"MeloTTS server request failed: {e}") from e

    data = resp.json()
    audio_b64 = data.get("audio_base64")
    mime_type = data.get("mime_type", "audio/wav")

    if not audio_b64:
        raise RuntimeError("MeloTTS server did not return audio_base64")

    return embed_audio_from_base64(audio_b64, mime_type=mime_type)
