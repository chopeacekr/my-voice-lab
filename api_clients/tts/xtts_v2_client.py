import base64
from pathlib import Path
import requests

XTTS_SERVER_URL = "http://127.0.0.1:8100"

def xtts_v2_tts_http(
    text: str,
    lang_code: str = "ko",
    speaker_wav_path: str | None = None,
    speed: float = 1.0,
) -> str:
    """XTTS v2 서버로 TTS 요청 (speaker_wav를 base64로 전송)"""
    url = f"{XTTS_SERVER_URL}/synthesize_base64"
    
    speaker_wav_b64 = None
    if speaker_wav_path:
        p = Path(speaker_wav_path)
        if p.exists() and p.stat().st_size > 0:
            speaker_wav_b64 = base64.b64encode(p.read_bytes()).decode("utf-8")
            print(f"📎 speaker_wav loaded: {speaker_wav_path}")
    
    payload = {
        "text": text,
        "lang": lang_code,
        "speed": speed,
        "speaker_wav_b64": speaker_wav_b64,
    }
    
    try:
        # 🔹 타임아웃 증가: 60 → 180초
        resp = requests.post(url, json=payload, timeout=180)
        resp.raise_for_status()
        
        data = resp.json()
        audio_b64 = data["audio_base64"]
        
        # HTML audio embed 생성
        html = f"""<audio controls>
    <source src="data:audio/wav;base64,{audio_b64}" type="audio/wav">
</audio>"""
        return html
        
    except requests.exceptions.Timeout as e:
        raise RuntimeError(f"XTTS v2 서버 타임아웃 (180초 초과): {e}") from e
    except Exception as e:
        raise RuntimeError(f"XTTS v2 server request failed: {e}") from e