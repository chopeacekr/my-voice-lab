"""
F5-TTS Client for my-voice-lab
Zero-shot Voice Cloning TTS
"""

import base64
import requests


def check_f5_health() -> dict:
    """
    F5-TTS 서버 상태 확인
    
    Returns:
        dict: 서버 상태 정보
    """
    try:
        response = requests.get("http://localhost:8500/health", timeout=5)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"❌ F5-TTS health check 실패: {e}")
        return {"status": "error", "message": str(e)}


def f5_tts_http(
    text: str,
    ref_audio_path: str | None = None,
    ref_text: str | None = None,
) -> str:
    """
    F5-TTS HTTP API를 통한 음성 합성
    
    Args:
        text: 생성할 텍스트
        ref_audio_path: 참조 음성 파일 경로 (선택)
        ref_text: 참조 음성의 텍스트 (선택)
    
    Returns:
        str: HTML audio 태그 또는 빈 문자열
    """
    url = "http://localhost:8500/synthesize"
    
    print(f"🔊 [F5-TTS] TTS 요청: {text[:30]}...")
    print(f"   - ref_audio: {ref_audio_path}")
    print(f"   - ref_text: {ref_text[:30] if ref_text else None}...")
    
    try:
        # Form data 준비 (files 형식으로 통일)
        files = {
            "text": (None, text),
        }
        
        # 참조 텍스트 추가
        if ref_text:
            files["ref_text"] = (None, ref_text)
        
        # 참조 음성 파일 추가
        if ref_audio_path:
            try:
                with open(ref_audio_path, "rb") as f:
                    files["ref_audio"] = (ref_audio_path, f.read(), "audio/wav")
            except Exception as e:
                print(f"⚠️ [F5-TTS] 참조 음성 파일 로드 실패: {e}")
        
        response = requests.post(
            url,
            files=files,
            timeout=300,  # F5-TTS는 처리 시간이 길 수 있음
        )
        response.raise_for_status()
        
        # 응답 확인
        audio_bytes = response.content
        print(f"✅ [F5-TTS] 성공! ({len(audio_bytes)} bytes)")
        
        if len(audio_bytes) < 100:
            print(f"⚠️ [F5-TTS] 오디오 데이터가 너무 작음: {len(audio_bytes)} bytes")
            print(f"   응답 내용: {audio_bytes[:100]}")
            return ""
        
        # Base64로 인코딩
        audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
        
        # HTML audio 태그 생성
        audio_html = f'<audio controls><source src="data:audio/wav;base64,{audio_b64}" type="audio/wav"></audio>'
        
        print(f"✅ [F5-TTS] HTML 태그 생성 완료")
        return audio_html
        
    except requests.exceptions.Timeout:
        print("❌ [F5-TTS] 타임아웃 (120초 초과)")
        print("💡 첫 실행 시 모델 로딩으로 시간이 오래 걸릴 수 있습니다.")
        return ""
    except requests.exceptions.RequestException as e:
        print(f"❌ [F5-TTS] 요청 실패: {e}")
        return ""
    except Exception as e:
        print(f"❌ [F5-TTS] 예외 발생: {e}")
        import traceback
        traceback.print_exc()
        return ""


if __name__ == "__main__":
    # 테스트
    print("=== F5-TTS Client 테스트 ===\n")
    
    # 1. Health check
    print("1. Health Check:")
    health = check_f5_health()
    print(f"   상태: {health}\n")
    
    # 2. 기본 음성 생성 (참조 없음)
    print("2. 기본 음성 생성 (참조 없음):")
    audio_html = f5_tts_http(text="안녕하세요, F5-TTS 테스트입니다.")
    print(f"   결과: {len(audio_html)} bytes\n")
    
    # 3. Voice Cloning (참조 음성 사용)
    print("3. Voice Cloning (참조 음성 사용):")
    audio_html = f5_tts_http(
        text="이것은 클로닝된 음성입니다.",
        ref_audio_path="my_voice1.wav",
        ref_text="안녕하세요, 반갑습니다."
    )
    print(f"   결과: {len(audio_html)} bytes\n")
    
    print("✅ 테스트 완료!")