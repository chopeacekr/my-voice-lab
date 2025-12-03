"""
Google Text-to-Speech (gTTS) Client
무료 클라우드 TTS - 서버 설치 불필요
"""

from gtts import gTTS
import io
import base64


def gtts_tts(text, lang_code="ko"):
    """
    Google Text-to-Speech를 사용한 음성 합성
    
    Args:
        text: 변환할 텍스트
        lang_code: 언어 코드 (예: 'ko', 'en', 'ja', 'zh-CN')
    
    Returns:
        str: Base64 인코딩된 HTML audio 태그
    
    Raises:
        RuntimeError: TTS 처리 중 오류 발생 시
    """
    try:
        print(f"🔊 [gTTS] Starting text-to-speech...")
        print(f"   - Language: {lang_code}")
        print(f"   - Text length: {len(text)} characters")
        print(f"   - Text preview: {text[:50]}...")
        
        # gTTS 객체 생성
        tts = gTTS(text=text, lang=lang_code, slow=False)
        
        # BytesIO에 저장
        audio_fp = io.BytesIO()
        tts.write_to_fp(audio_fp)
        audio_fp.seek(0)
        audio_bytes = audio_fp.read()
        
        print(f"   ✅ TTS successful!")
        print(f"   📊 Audio size: {len(audio_bytes)} bytes")
        
        # Base64 인코딩
        audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
        
        # HTML audio 태그 생성
        audio_html = f'<audio controls><source src="data:audio/mp3;base64,{audio_b64}" type="audio/mp3"></audio>'
        
        return audio_html
        
    except Exception as e:
        error_msg = f"gTTS processing failed: {e}"
        print(f"   ❌ {error_msg}")
        
        print("\n   💡 Possible reasons:")
        print("      1. No internet connection")
        print("      2. Invalid language code")
        print("      3. Text too long (> 5000 characters)")
        print("      4. Google TTS API temporarily unavailable")
        
        print("\n   🔧 Suggestions:")
        print("      - Check internet connection")
        print("      - Verify language code")
        print("      - Shorten text if too long")
        
        raise RuntimeError(error_msg)


def get_supported_languages():
    """
    gTTS 지원 언어 목록 반환
    
    Returns:
        dict: 언어 이름 -> 언어 코드 매핑
    """
    return {
        "Korean": "ko",
        "English": "en",
        "Japanese": "ja",
        "Chinese (Simplified)": "zh-CN",
        "Chinese (Traditional)": "zh-TW",
        "French": "fr",
        "German": "de",
        "Spanish": "es",
        "Italian": "it",
        "Portuguese": "pt",
        "Russian": "ru",
        "Arabic": "ar",
        "Hindi": "hi",
        "Thai": "th",
        "Vietnamese": "vi",
        "Turkish": "tr",
        "Polish": "pl",
        "Dutch": "nl",
        "Indonesian": "id",
    }


# 테스트 코드
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python gTTS_client.py <text> [lang_code]")
        print("\nSupported languages:")
        for lang_name, lang_code in get_supported_languages().items():
            print(f"  {lang_name}: {lang_code}")
        sys.exit(1)
    
    text = sys.argv[1]
    lang_code = sys.argv[2] if len(sys.argv) > 2 else "ko"
    
    # TTS 실행
    try:
        result = gtts_tts(text, lang_code=lang_code)
        print(f"\n✅ Success!")
        print(f"HTML Audio Tag Length: {len(result)} characters")
    except RuntimeError as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)