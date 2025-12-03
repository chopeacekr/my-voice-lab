import base64
from tempfile import NamedTemporaryFile
import io

import streamlit as st
from audiorecorder import audiorecorder
from langchain_google_genai import ChatGoogleGenerativeAI
from pydub import AudioSegment

from api_clients.melotts_client import melotts_tts_http
from api_clients.xtts_v2_client import xtts_v2_tts_http
from api_clients.bark_client import bark_tts_http, check_bark_health
from api_clients.f5_client import f5_tts_http, check_f5_health
from api_clients.vosk_client import vosk_stt_http, check_vosk_health
from api_clients.whisper_client import whisper_stt_http, check_whisper_health
from api_clients.gSR_client import google_sr_stt
from api_clients.wav2vec2_client import wav2vec2_stt_http, check_wav2vec2_health


# ================================
# 언어 설정
# ================================
SUPPORTED_LANGUAGES = {
    "Korean":  {"code": "ko", "llm": "Korean", "melo": "KR", "vosk": "KR", "whisper": "KR", "gsr": "ko-KR", "wav2vec2": "KR", "bark": "KR", "f5": "KR"},
    "English": {"code": "en", "llm": "English", "melo": "EN", "vosk": "EN", "whisper": "EN", "gsr": "en-US", "wav2vec2": "EN", "bark": "EN", "f5": "EN"},
    "Japanese": {"code": "ja", "llm": "Japanese", "melo": "JP", "vosk": "JP", "whisper": "JP", "gsr": "ja-JP", "wav2vec2": "JP", "bark": "JP", "f5": "JP"},
    "French": {"code": "fr", "llm": "French", "melo": "FR", "vosk": "FR", "whisper": "FR", "gsr": "fr-FR", "wav2vec2": "FR", "bark": "FR", "f5": "FR"},
    "German": {"code": "de", "llm": "German", "melo": None, "vosk": "DE", "whisper": "DE", "gsr": "de-DE", "wav2vec2": "DE", "bark": "DE", "f5": "DE"},
    "Spanish": {"code": "es", "llm": "Spanish", "melo": "ES", "vosk": "ES", "whisper": "ES", "gsr": "es-ES", "wav2vec2": "ES", "bark": "ES", "f5": "ES"},
    "Italian": {"code": "it", "llm": "Italian", "melo": None, "vosk": None, "whisper": None, "gsr": "it-IT", "wav2vec2": None, "bark": "IT", "f5": "IT"},
    "Portuguese": {"code": "pt", "llm": "Portuguese", "melo": None, "vosk": None, "whisper": None, "gsr": "pt-PT", "wav2vec2": None, "bark": "PT", "f5": "PT"},
    "Polish": {"code": "pl", "llm": "Polish", "melo": None, "vosk": None, "whisper": None, "gsr": "pl-PL", "wav2vec2": None, "bark": "PL", "f5": None},
    "Turkish": {"code": "tr", "llm": "Turkish", "melo": None, "vosk": None, "whisper": None, "gsr": "tr-TR", "wav2vec2": None, "bark": "TR", "f5": None},
    "Russian": {"code": "ru", "llm": "Russian", "melo": None, "vosk": "RU", "whisper": "RU", "gsr": "ru-RU", "wav2vec2": "RU", "bark": "RU", "f5": None},
    "Dutch": {"code": "nl", "llm": "Dutch", "melo": None, "vosk": None, "whisper": None, "gsr": "nl-NL", "wav2vec2": None, "bark": None, "f5": None},
    "Chinese": {"code": "zh", "llm": "Chinese", "melo": "ZH", "vosk": "ZH", "whisper": "ZH", "gsr": "zh-CN", "wav2vec2": "ZH", "bark": "ZH", "f5": "ZH"},
    "Hindi": {"code": "hi", "llm": "Hindi", "melo": None, "vosk": None, "whisper": None, "gsr": "hi-IN", "wav2vec2": None, "bark": "HI", "f5": None},
}


def language_names():
    return list(SUPPORTED_LANGUAGES.keys())


# ================================
# TTS 모델 레지스트리
# ================================
TTS_MODEL_REGISTRY = {
    "melotts": {
        "label": "MeloTTS (Fast & Multilingual)",
        "type": "melotts",
        "description": "빠른 다국어 음성 합성 (1-2초)",
        "features": ["빠른 처리", "다국어"],
    },
    "xtts_v2": {
        "label": "XTTS v2 (Voice Cloning)",
        "type": "xtts_v2",
        "description": "고품질 Voice Cloning (5-10초)",
        "features": ["Voice Cloning", "고품질"],
    },
    "f5_tts": {
        "label": "F5-TTS (Zero-shot Voice Cloning)",
        "type": "f5_tts",
        "description": "최고 품질 Zero-shot Voice Cloning (10-20초)",
        "features": ["Zero-shot", "최고 품질", "자연스러움"],
    },
    "bark": {
        "label": "Bark (Expressive & Emotional)",
        "type": "bark",
        "description": "표현력 높은 감정 음성 합성 (100-200초)",
        "features": ["감정 표현", "음악/효과음", "100+ 화자"],
    },
}


# ================================
# STT 모델 레지스트리
# ================================
STT_MODEL_REGISTRY = {
    "whisper": {
        "label": "Whisper (Accurate STT)",
        "type": "whisper",
    },
    "wav2vec2": {
        "label": "Wav2Vec2 (Korean Optimized)",
        "type": "wav2vec2",
    },
    "google_sr": {
        "label": "Google SR (Cloud STT)",
        "type": "google_sr",
    },
    "vosk": {
        "label": "Vosk (Offline STT)",
        "type": "vosk",
    },
}


def get_tts_model_key_from_label(label: str) -> str:
    for key, cfg in TTS_MODEL_REGISTRY.items():
        if cfg["label"] == label:
            return key
    raise ValueError(f"Unknown TTS model label: {label}")


def get_stt_model_key_from_label(label: str) -> str:
    for key, cfg in STT_MODEL_REGISTRY.items():
        if cfg["label"] == label:
            return key
    raise ValueError(f"Unknown STT model label: {label}")


# ================================
# 세션 상태 초기화
# ================================
DEFAULT_SPEAKER_WAV = "my_voice1.wav"

if "messages" not in st.session_state:
    st.session_state.messages = []

if "speaker_path" not in st.session_state:
    st.session_state.speaker_path = DEFAULT_SPEAKER_WAV

if "tts_model_key" not in st.session_state:
    st.session_state.tts_model_key = "melotts"

if "stt_model_key" not in st.session_state:
    st.session_state.stt_model_key = "whisper"

# Bark 전용 설정
if "bark_voice_preset" not in st.session_state:
    st.session_state.bark_voice_preset = None

if "bark_speed" not in st.session_state:
    st.session_state.bark_speed = 1.0

# F5-TTS 전용 설정
if "f5_ref_audio_path" not in st.session_state:
    st.session_state.f5_ref_audio_path = "my_voice1.wav"  # ⭐ 기본 참조 음성

if "f5_ref_text" not in st.session_state:
    st.session_state.f5_ref_text = ""

if "f5_use_reference" not in st.session_state:
    st.session_state.f5_use_reference = True  # ⭐ 기본값 True

if "autoplay_index" not in st.session_state:
    st.session_state.autoplay_index = None

if "prompt_text" not in st.session_state:
    st.session_state.prompt_text = ""

if "stt_processed" not in st.session_state:
    st.session_state.stt_processed = False

if "recorder_key_counter" not in st.session_state:
    st.session_state.recorder_key_counter = 0


# ================================
# 오디오 전처리
# ================================
def preprocess_audio_for_stt(audio_segment: AudioSegment, target_sample_rate: int = 16000) -> bytes:
    if audio_segment.channels > 1:
        audio_segment = audio_segment.set_channels(1)
    
    if audio_segment.frame_rate != target_sample_rate:
        audio_segment = audio_segment.set_frame_rate(target_sample_rate)
    
    buffer = io.BytesIO()
    audio_segment.export(buffer, format="wav")
    return buffer.getvalue()


# ================================
# TTS inference
# ================================
def tts_inference(
    model_key: str,
    text: str | None,
    speaker_path: str | None,
    lang_code: str,
    melo_lang_code: str | None = None,
    bark_lang_code: str | None = None,
    bark_voice_preset: str | None = None,
    bark_speed: float = 1.0,
    f5_lang_code: str | None = None,
    f5_ref_audio_path: str | None = None,
    f5_ref_text: str | None = None,
) -> str:
    if text is None:
        return ""
    text = text.strip()
    if not text:
        return ""

    cfg = TTS_MODEL_REGISTRY[model_key]
    model_type = cfg["type"]

    # MeloTTS
    if model_type == "melotts":
        if not melo_lang_code:
            print("⚠ MeloTTS: melo_lang_code is None, skipping TTS")
            return ""
        print(f"👉 MeloTTS via HTTP: language={melo_lang_code}")
        return melotts_tts_http(
            text=text,
            melo_lang_code=melo_lang_code,
            speed=1.0,
            speaker=None,
        )

    # XTTS v2
    if model_type == "xtts_v2":
        print(f"👉 XTTS v2 via HTTP: language={lang_code}")
        return xtts_v2_tts_http(
            text=text,
            lang_code=lang_code,
            speaker_wav_path=speaker_path,
            speed=1.0,
        )

    # F5-TTS
    if model_type == "f5_tts":
        if not f5_lang_code:
            print("⚠ F5-TTS: f5_lang_code is None, using default")
        
        # ⭐ F5-TTS는 참조 음성이 필수! None이면 my_voice1.wav 사용
        if not f5_ref_audio_path:
            f5_ref_audio_path = "my_voice1.wav"
            print("⚠ F5-TTS: ref_audio is None, using default (my_voice1.wav)")
        
        print(f"👉 F5-TTS via HTTP: language={f5_lang_code}, ref_audio={f5_ref_audio_path}, ref_text={f5_ref_text}")
        return f5_tts_http(
            text=text,
            ref_audio_path=f5_ref_audio_path,
            ref_text=f5_ref_text,
        )

    # Bark
    if model_type == "bark":
        if not bark_lang_code:
            print("⚠ Bark: bark_lang_code is None, using default")
        print(f"👉 Bark via HTTP: language={bark_lang_code}, preset={bark_voice_preset}, speed={bark_speed}")
        return bark_tts_http(
            text=text,
            voice_preset=bark_voice_preset,
            speed=bark_speed,
        )

    print(f"⚠ Unsupported model type for inference: {model_type}")
    return ""


# ================================
# STT inference
# ================================
def stt_inference(
    model_key: str,
    audio_bytes: bytes,
    vosk_lang_code: str | None = None,
    whisper_lang_code: str | None = None,
    gsr_lang_code: str | None = None,
    wav2vec2_lang_code: str | None = None,
) -> str:
    print(f"\n🔊 [DEBUG] stt_inference 호출")
    print(f"   - model_key: {model_key}")
    print(f"   - audio_bytes 크기: {len(audio_bytes)} bytes")
    
    cfg = STT_MODEL_REGISTRY[model_key]
    model_type = cfg["type"]
    print(f"   - model_type: {model_type}")

    if model_type == "vosk":
        if not vosk_lang_code:
            raise ValueError("Vosk requires vosk_lang_code")
        return vosk_stt_http(
            audio_bytes=audio_bytes,
            lang=vosk_lang_code,
            sample_rate=16000,
        )

    if model_type == "whisper":
        if not whisper_lang_code:
            whisper_lang_code = "KR"
        return whisper_stt_http(
            audio_bytes=audio_bytes,
            lang=whisper_lang_code,
            sample_rate=16000,
        )

    if model_type == "google_sr":
        if not gsr_lang_code:
            gsr_lang_code = "ko-KR"
        return google_sr_stt(
            audio_bytes=audio_bytes,
            lang_code=gsr_lang_code,
        )

    if model_type == "wav2vec2":
        if not wav2vec2_lang_code:
            wav2vec2_lang_code = "KR"
        return wav2vec2_stt_http(
            audio_bytes=audio_bytes,
            lang=wav2vec2_lang_code,
            sample_rate=16000,
        )

    raise ValueError(f"Unsupported STT model type: {model_type}")


# ================================
# 채팅 히스토리 유틸
# ================================
def clear_history():
    st.session_state.messages = []


def rewind():
    if st.session_state.messages:
        msg = st.session_state.messages.pop()
        while st.session_state.messages and msg.get("role", "") != "user":
            msg = st.session_state.messages.pop()


# ================================
# Streamlit UI
# ================================
st.title("🎙️ Peace Chatbot System (Gemini + Multi-TTS/STT)")

with st.sidebar:
    # ========== TTS 모델 선택 ==========
    st.header("🔊 TTS Model")

    tts_model_keys = list(TTS_MODEL_REGISTRY.keys())
    tts_model_labels = [TTS_MODEL_REGISTRY[k]["label"] for k in tts_model_keys]

    try:
        tts_default_index = tts_model_keys.index(st.session_state.tts_model_key)
    except ValueError:
        tts_default_index = 0

    tts_model_label = st.selectbox(
        "TTS Model",
        tts_model_labels,
        index=tts_default_index,
    )
    tts_model_key = get_tts_model_key_from_label(tts_model_label)
    st.session_state.tts_model_key = tts_model_key

    # 모델 설명
    tts_cfg = TTS_MODEL_REGISTRY[tts_model_key]
    st.caption(f"📝 {tts_cfg['description']}")
    st.caption(f"✨ {', '.join(tts_cfg['features'])}")

    # F5-TTS 전용 옵션
    if tts_model_key == "f5_tts":
        st.markdown("---")
        st.subheader("🎤 F5-TTS 옵션")
        
        st.info("💡 F5-TTS는 참조 음성이 필수입니다. 기본: my_voice1.wav")
        
        st.session_state.f5_use_reference = st.checkbox(
            "참조 음성 사용",
            value=st.session_state.f5_use_reference,
            help="F5-TTS는 항상 참조 음성을 사용합니다. 체크 해제 시 기본(my_voice1.wav) 사용"
        )
        
        if st.session_state.f5_use_reference:
            st.caption("📂 현재 참조 음성")
            if st.session_state.f5_ref_audio_path:
                ref_name = st.session_state.f5_ref_audio_path.split("/")[-1]
                if ref_name == "my_voice1.wav":
                    st.info(f"✅ 기본: {ref_name}")
                else:
                    st.success(f"✅ 커스텀: {ref_name}")
            else:
                st.warning("⚠️ 참조 없음 → my_voice1.wav 사용")
                st.session_state.f5_ref_audio_path = "my_voice1.wav"
            
            st.session_state.f5_ref_text = st.text_area(
                "참조 음성의 텍스트 (선택)",
                value=st.session_state.f5_ref_text,
                height=80,
                help="참조 음성이 말한 내용 (선택사항)",
                placeholder="예: 안녕하세요, 반갑습니다."
            )
            
            if st.button("🔄 기본 참조로 초기화", use_container_width=True):
                st.session_state.f5_ref_audio_path = "my_voice1.wav"
                st.session_state.f5_ref_text = ""
                st.success("✅ my_voice1.wav로 초기화!")
                st.rerun()
        else:
            st.info("💡 기본 참조(my_voice1.wav) 사용")
            st.session_state.f5_ref_audio_path = "my_voice1.wav"
        
        try:
            health = check_f5_health()
            if health.get("status") == "ok":
                st.success("✅ F5-TTS Server Connected (Port 8500)")
                model = health.get("model")
                device = health.get("device")
                if model and device:
                    st.caption(f"🎤 {model} • {device}")
            else:
                st.error("❌ F5-TTS Server Error")
        except:
            st.error("❌ F5-TTS Server Offline")
            st.info("💡 my_f5 디렉토리에서 서버를 시작하세요:\n`python server_tts.py`")

    # Bark 전용 옵션
    elif tts_model_key == "bark":
        st.markdown("---")
        st.subheader("🐶 Bark 옵션")
        
        st.warning("⚠️ Bark는 처리 시간이 매우 깁니다 (100-200초). 첫 요청은 더 오래 걸릴 수 있습니다.")
        
        voice_preset_options = {
            "기본 (자동)": None,
            "영어-남성1": "v2/en_speaker_0",
            "영어-여성1": "v2/en_speaker_1",
            "영어-남성2": "v2/en_speaker_2",
            "한국어-남성1": "v2/ko_speaker_0",
            "한국어-여성1": "v2/ko_speaker_1",
            "한국어-남성2": "v2/ko_speaker_2",
            "중국어-남성1": "v2/zh_speaker_0",
            "중국어-여성1": "v2/zh_speaker_1",
        }
        
        voice_preset_display = st.selectbox(
            "화자 프리셋",
            options=list(voice_preset_options.keys()),
            help="100개 이상의 화자 중 일부. 언어에 맞는 화자를 선택하세요."
        )
        st.session_state.bark_voice_preset = voice_preset_options[voice_preset_display]
        
        st.session_state.bark_speed = st.slider(
            "음성 속도",
            min_value=0.5,
            max_value=2.0,
            value=1.0,
            step=0.1,
            help="0.5x (느림) ~ 2.0x (빠름)"
        )
        
        with st.expander("📝 특수 토큰 사용법"):
            st.markdown("""
            **감정 표현:**
            - `[laughs]` - 웃음 😄
            - `[sighs]` - 한숨 😔
            - `[cries]` - 울음 😢
            - `[gasps]` - 헐떡임 😲
            
            **효과음:**
            - `[music]` - 음악/노래 🎵
            - `[applause]` - 박수 👏
            
            **사용 예시:**
            - "정말 기쁩니다! [laughs]"
            - "오늘은 힘드네요... [sighs]"
            - "생일 축하합니다! ♪ [music]"
            """)
        
        try:
            health = check_bark_health()
            if health.get("status") == "ok":
                st.success("✅ Bark Server Connected (Port 8600)")
                model_loaded = health.get("model_loaded")
                device = health.get("device")
                sample_rate = health.get("sample_rate")
                if model_loaded and device:
                    st.caption(f"🎤 {device} • {sample_rate}Hz")
            else:
                st.error("❌ Bark Server Error")
        except:
            st.error("❌ Bark Server Offline")
            st.info("💡 my_bark 디렉토리에서 서버를 시작하세요:\n`uv run python server_tts.py`")

    # ========== STT 모델 선택 ==========
    st.markdown("---")
    st.header("🎤 STT Model")

    stt_model_keys = list(STT_MODEL_REGISTRY.keys())
    stt_model_labels = [STT_MODEL_REGISTRY[k]["label"] for k in stt_model_keys]

    try:
        stt_default_index = stt_model_keys.index(st.session_state.stt_model_key)
    except ValueError:
        stt_default_index = 0

    stt_model_label = st.selectbox(
        "STT Model",
        stt_model_labels,
        index=stt_default_index,
    )
    stt_model_key = get_stt_model_key_from_label(stt_model_label)
    
    if st.session_state.stt_model_key != stt_model_key:
        print(f"\n🔄 [DEBUG] STT 모델 변경: {st.session_state.stt_model_key} → {stt_model_key}")
    
    st.session_state.stt_model_key = stt_model_key

    # STT 서버 상태
    if stt_model_key == "vosk":
        try:
            health = check_vosk_health()
            if health.get("status") == "ok":
                st.success("✅ Vosk STT Server Connected")
                loaded = health.get("loaded_languages", [])
                if loaded:
                    st.caption(f"Loaded: {', '.join(loaded)}")
            else:
                st.error("❌ Vosk STT Server Error")
        except:
            st.error("❌ Vosk STT Server Offline")
    
    elif stt_model_key == "whisper":
        try:
            health = check_whisper_health()
            if health.get("status") == "ok":
                st.success("✅ Whisper STT Server Connected")
                model = health.get("model", "")
                device = health.get("device", "")
                if model and device:
                    st.caption(f"Model: {model} ({device})")
            else:
                st.error("❌ Whisper STT Server Error")
        except:
            st.error("❌ Whisper STT Server Offline")
    
    elif stt_model_key == "wav2vec2":
        try:
            health = check_wav2vec2_health()
            if health.get("status") == "ok":
                st.success("✅ Wav2Vec2 STT Server Connected")
                model_id = health.get("model_id", "")
                device = health.get("device", "")
                if model_id:
                    st.caption(f"Model: {model_id.split('/')[-1]}")
                if device:
                    st.caption(f"Device: {device}")
            else:
                st.error("❌ Wav2Vec2 STT Server Error")
        except:
            st.error("❌ Wav2Vec2 STT Server Offline (Port 8400)")
    
    elif stt_model_key == "google_sr":
        st.success("✅ Google SR (Local Processing)")
        st.caption("No server required • Internet connection needed")

    # ========== 언어 선택 ==========
    st.markdown("---")
    st.header("🌍 Language")
    lang_display = st.selectbox("Language", language_names())
    lang_info = SUPPORTED_LANGUAGES[lang_display]
    lang_code = lang_info["code"]
    lang_for_llm = lang_info["llm"]
    melo_lang_code = lang_info.get("melo")
    vosk_lang_code = lang_info.get("vosk")
    whisper_lang_code = lang_info.get("whisper")
    gsr_lang_code = lang_info.get("gsr")
    wav2vec2_lang_code = lang_info.get("wav2vec2")
    bark_lang_code = lang_info.get("bark")
    f5_lang_code = lang_info.get("f5")

    # 언어 지원 경고
    if tts_model_key == "melotts" and not melo_lang_code:
        st.warning(
            f"⚠️ MeloTTS does not support {lang_display}. "
            "Please select another language or use XTTS v2/F5-TTS/Bark."
        )
    
    if tts_model_key == "f5_tts" and not f5_lang_code:
        st.warning(
            f"⚠️ F5-TTS does not support {lang_display}. "
            "Please select another language."
        )
    
    if tts_model_key == "bark" and not bark_lang_code:
        st.warning(
            f"⚠️ Bark does not support {lang_display}. "
            "Please select another language."
        )

    if stt_model_key == "vosk" and not vosk_lang_code:
        st.warning(f"⚠️ Vosk does not support {lang_display} STT.")
    
    if stt_model_key == "whisper" and not whisper_lang_code:
        st.warning(f"⚠️ Whisper does not support {lang_display} STT.")
    
    if stt_model_key == "wav2vec2" and not wav2vec2_lang_code:
        st.warning(f"⚠️ Wav2Vec2 does not support {lang_display} STT.")

    # ========== 컨트롤 ==========
    st.markdown("---")
    st.header("⚙️ Control")
    gemini_api_key = st.text_input(
        "GEMINI API Key",
        key="chatbot_api_key",
        type="password",
    )

    llm_max_chars = st.number_input(
        "LLM 요약 최대 글자 수",
        min_value=50,
        max_value=1000,
        value=300,
        step=50,
    )

    voice_embed = st.toggle("Show Audio", value=True)
    btn_col1, btn_col2 = st.columns(2)
    with btn_col1:
        st.button("Rewind", on_click=rewind, use_container_width=True, type="primary")
    with btn_col2:
        st.button("Clear", on_click=clear_history, use_container_width=True)

    st.markdown("---")
    if tts_model_key == "xtts_v2":
        st.write("**XTTS v2 화자 레퍼런스:**")
        st.code(st.session_state.speaker_path or "기본 화자 (my_voice1.wav)", language="bash")
    elif tts_model_key == "f5_tts":
        st.info("🎤 F5-TTS는 참조 음성을 사용합니다. 위에서 설정하세요.")
    elif tts_model_key == "bark":
        st.info("🐶 Bark는 화자 프리셋을 사용합니다. 위에서 선택하세요.")
    else:
        st.info("ℹ️ MeloTTS는 화자 레퍼런스를 사용하지 않습니다.")


# ================================
# 녹음 UI (XTTS/F5-TTS speaker reference)
# ================================
st.subheader("🎤 Record your voice sample (for XTTS/F5-TTS speaker reference)")

audio = audiorecorder("녹음시작", "녹음정지", key="voice_recorder")

if len(audio) > 0:
    st.success("Recording complete!")
    with NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
        tmp_path = tmp_file.name
        audio.export(tmp_path, format="wav")
        st.write(f"저장된 파일: {tmp_path}")
        st.session_state.speaker_path = tmp_path
        
        # F5-TTS 참조 음성으로도 설정
        if tts_model_key == "f5_tts":
            st.session_state.f5_ref_audio_path = tmp_path
            st.info("💡 F5-TTS 참조 음성으로 설정되었습니다.")

st.caption(
    "※ XTTS v2와 F5-TTS를 사용할 때 이 음성을 화자 레퍼런스로 사용합니다. "
    "MeloTTS와 Bark를 사용할 때는 참고용으로만 저장됩니다."
)


# ================================
# 히스토리 표시
# ================================
autoplay_index = st.session_state.autoplay_index

for i, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        content = msg.get("content", "")
        if voice_embed:
            embed = msg.get("tts_embed", "")
            if embed and autoplay_index is not None and i == autoplay_index:
                embed = embed.replace("<audio controls>", "<audio controls autoplay>")
            if embed:
                content = "\n\n".join([content, embed])
        st.markdown(content, unsafe_allow_html=True)

st.session_state.autoplay_index = None


# ================================
# 채팅 입력 처리
# ================================
st.subheader("💬 Chat Input")

col1, col2 = st.columns([5, 1])

# 음성 녹음
with col2:
    stt_available = False
    
    if stt_model_key == "vosk" and vosk_lang_code:
        stt_available = True
    elif stt_model_key == "whisper" and whisper_lang_code:
        stt_available = True
    elif stt_model_key == "google_sr" and gsr_lang_code:
        stt_available = True
    elif stt_model_key == "wav2vec2" and wav2vec2_lang_code:
        stt_available = True
    
    if stt_available:
        audio_stt = audiorecorder("🎤", "⏹️", key=f"stt_recorder_{st.session_state.recorder_key_counter}")
    else:
        audio_stt = None
        st.caption("STT 미지원")

# 음성 입력 처리
prompt = None

if audio_stt and len(audio_stt) > 0 and not st.session_state.stt_processed:
    st.info("🎤 음성 입력 감지됨. 텍스트로 변환 중...")
    
    with st.spinner("Converting speech to text..."):
        try:
            audio_bytes = preprocess_audio_for_stt(audio_stt, target_sample_rate=16000)
            st.caption(f"📊 Audio preprocessed: {len(audio_bytes)} bytes")
            
            transcribed_text = stt_inference(
                model_key=st.session_state.stt_model_key,
                audio_bytes=audio_bytes,
                vosk_lang_code=vosk_lang_code,
                whisper_lang_code=whisper_lang_code,
                gsr_lang_code=gsr_lang_code,
                wav2vec2_lang_code=wav2vec2_lang_code,
            )
            
            if transcribed_text.strip():
                st.success(f"✅ 인식된 텍스트: {transcribed_text}")
                st.session_state.prompt_text = transcribed_text
                st.session_state.stt_processed = True
                st.session_state.recorder_key_counter += 1
                st.session_state.stt_processed = False
                st.rerun()
            else:
                st.warning("⚠️ 음성이 인식되지 않았습니다. 다시 시도해주세요.")
                st.session_state.recorder_key_counter += 1
                st.session_state.stt_processed = False
                
        except Exception as e:
            st.error(f"❌ STT 처리 실패: {e}")
            
            if stt_model_key == "google_sr":
                st.info("💡 Google SR: 인터넷 연결 확인")
            elif stt_model_key == "wav2vec2":
                st.info("💡 Wav2Vec2: 서버 실행 확인 (포트 8400)")
            
            st.session_state.recorder_key_counter += 1
            st.session_state.stt_processed = False

# 텍스트 입력
with col1:
    prompt_text = st.text_area(
        "Your message",
        value=st.session_state.prompt_text,
        height=80,
    )
    
    if prompt_text != st.session_state.prompt_text:
        st.session_state.prompt_text = prompt_text

# Send 버튼과 TTS 전용 버튼
col_send1, col_send2 = st.columns([1, 1])
with col_send1:
    send_clicked = st.button("Send (LLM + TTS)", type="primary", use_container_width=True)
with col_send2:
    tts_only_clicked = st.button("🔊 TTS Only", use_container_width=True)

# TTS Only 버튼 처리 (LLM 없이 TTS만 테스트)
if tts_only_clicked and st.session_state.prompt_text and st.session_state.prompt_text.strip():
    test_text = st.session_state.prompt_text.strip()
    
    with st.chat_message("assistant"):
        st.markdown(f"**🔊 TTS 테스트:** {test_text}")
        
        # TTS 모델 언어 지원 확인
        if tts_model_key == "f5_tts" and not f5_lang_code:
            st.error(f"F5-TTS does not support {lang_display}.")
            tts_embed = ""
        elif tts_model_key == "bark" and not bark_lang_code:
            st.error(f"Bark does not support {lang_display}.")
            tts_embed = ""
        elif tts_model_key == "melotts" and not melo_lang_code:
            st.error(f"MeloTTS does not support {lang_display}.")
            tts_embed = ""
        else:
            # Bark 사용 시 처리 시간 경고
            if tts_model_key == "bark":
                with st.spinner("🐶 Bark 음성 생성 중... (100-200초 소요, 첫 실행은 더 오래 걸립니다)"):
                    try:
                        tts_embed = tts_inference(
                            model_key=st.session_state.tts_model_key,
                            text=test_text,
                            speaker_path=st.session_state.speaker_path,
                            lang_code=lang_code,
                            melo_lang_code=melo_lang_code,
                            bark_lang_code=bark_lang_code,
                            bark_voice_preset=st.session_state.bark_voice_preset,
                            bark_speed=st.session_state.bark_speed,
                            f5_lang_code=f5_lang_code,
                            f5_ref_audio_path=st.session_state.f5_ref_audio_path if st.session_state.f5_use_reference else "my_voice1.wav",
                            f5_ref_text=st.session_state.f5_ref_text if st.session_state.f5_use_reference else None,
                        )
                    except Exception as e:
                        st.error(f"⚠️ TTS 생성 실패: {e}")
                        st.info("💡 Bark 서버가 실행 중인지 확인하세요 (포트 8600)")
                        tts_embed = ""
            else:
                with st.spinner(f"🎤 {tts_cfg['label']} 음성 생성 중..."):
                    try:
                        tts_embed = tts_inference(
                            model_key=st.session_state.tts_model_key,
                            text=test_text,
                            speaker_path=st.session_state.speaker_path,
                            lang_code=lang_code,
                            melo_lang_code=melo_lang_code,
                            bark_lang_code=bark_lang_code,
                            bark_voice_preset=st.session_state.bark_voice_preset,
                            bark_speed=st.session_state.bark_speed,
                            f5_lang_code=f5_lang_code,
                            f5_ref_audio_path=st.session_state.f5_ref_audio_path if st.session_state.f5_use_reference else "my_voice1.wav",
                            f5_ref_text=st.session_state.f5_ref_text if st.session_state.f5_use_reference else None,
                        )
                    except Exception as e:
                        st.error(f"⚠️ TTS 생성 실패: {e}")
                        st.info("💡 서버가 실행 중인지 확인하세요")
                        tts_embed = ""
            
            if tts_embed:
                st.markdown(tts_embed, unsafe_allow_html=True)
                st.success("✅ TTS 테스트 완료!")
    
    # 입력창 초기화 (선택 사항)
    # st.session_state.prompt_text = ""
    # st.rerun()

# 프롬프트 처리
if send_clicked and st.session_state.prompt_text and st.session_state.prompt_text.strip():
    prompt = st.session_state.prompt_text.strip()

    with st.chat_message("user"):
        st.markdown(prompt, unsafe_allow_html=True)

    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        with st.spinner("Generating response..."):
            if not gemini_api_key:
                st.error("GEMINI API Key를 먼저 입력해주세요.")
                llm_response = ""
                tts_embed = ""
            else:
                if not gemini_api_key.startswith("AIza"):
                    st.error("⚠️ Gemini API 키 형식이 올바르지 않습니다.")
                    llm_response = ""
                    tts_embed = ""
                elif tts_model_key == "f5_tts" and not f5_lang_code:
                    st.error(f"F5-TTS does not support {lang_display}.")
                    llm_response = ""
                    tts_embed = ""
                elif tts_model_key == "bark" and not bark_lang_code:
                    st.error(f"Bark does not support {lang_display}.")
                    llm_response = ""
                    tts_embed = ""
                elif tts_model_key == "melotts" and not melo_lang_code:
                    st.error(f"MeloTTS does not support {lang_display}.")
                    llm_response = ""
                    tts_embed = ""
                else:
                    try:
                        llm = ChatGoogleGenerativeAI(
                            model="gemini-2.5-flash",
                            temperature=0,
                            max_tokens=1024,
                            google_api_key=gemini_api_key,
                        )
                    except Exception as e:
                        st.error(f"❌ LLM 초기화 실패: {e}")
                        llm_response = ""
                        tts_embed = ""
                    else:
                        try:
                            raw_resp = llm.invoke(
                                prompt
                                + f"\nPlease answer in {lang_for_llm}, and keep it short, under {llm_max_chars} characters."
                            ).content
                        except Exception as e:
                            error_msg = str(e)
                            if "429" in error_msg or "quota" in error_msg.lower():
                                st.error("⚠️ Gemini API 할당량 초과")
                                st.info("💡 잠시 후 다시 시도해주세요.")
                            else:
                                st.error(f"❌ LLM 요청 실패: {e}")
                            raw_resp = None

                        llm_response = (raw_resp or "").strip()

                        if not llm_response:
                            st.warning("LLM 응답이 비어 있어 TTS를 건너뜁니다.")
                            tts_embed = ""
                        else:
                            st.markdown(llm_response)
                            
                            # Bark 사용 시 처리 시간 경고
                            if tts_model_key == "bark":
                                with st.spinner("🐶 Bark 음성 생성 중... (100-200초 소요, 첫 실행은 더 오래 걸립니다)"):
                                    try:
                                        tts_embed = tts_inference(
                                            model_key=st.session_state.tts_model_key,
                                            text=llm_response,
                                            speaker_path=st.session_state.speaker_path,
                                            lang_code=lang_code,
                                            melo_lang_code=melo_lang_code,
                                            bark_lang_code=bark_lang_code,
                                            bark_voice_preset=st.session_state.bark_voice_preset,
                                            bark_speed=st.session_state.bark_speed,
                                            f5_lang_code=f5_lang_code,
                                            f5_ref_audio_path=st.session_state.f5_ref_audio_path if st.session_state.f5_use_reference else "my_voice1.wav",
                                            f5_ref_text=st.session_state.f5_ref_text if st.session_state.f5_use_reference else None,
                                        )
                                    except Exception as e:
                                        st.error(f"⚠️ TTS 생성 실패: {e}")
                                        st.info("💡 Bark 서버가 실행 중인지 확인하세요 (포트 8600)")
                                        tts_embed = ""
                            else:
                                current_speaker = st.session_state.speaker_path
                                try:
                                    tts_embed = tts_inference(
                                        model_key=st.session_state.tts_model_key,
                                        text=llm_response,
                                        speaker_path=current_speaker,
                                        lang_code=lang_code,
                                        melo_lang_code=melo_lang_code,
                                        bark_lang_code=bark_lang_code,
                                        bark_voice_preset=st.session_state.bark_voice_preset,
                                        bark_speed=st.session_state.bark_speed,
                                        f5_lang_code=f5_lang_code,
                                        f5_ref_audio_path=st.session_state.f5_ref_audio_path if st.session_state.f5_use_reference else "my_voice1.wav",
                                        f5_ref_text=st.session_state.f5_ref_text if st.session_state.f5_use_reference else None,
                                    )
                                except Exception as e:
                                    st.error(f"⚠️ TTS 생성 실패: {e}")
                                    st.info("💡 첫 요청은 모델 로딩으로 시간이 오래 걸릴 수 있습니다.")
                                    tts_embed = ""

                            if tts_embed:
                                st.markdown(tts_embed, unsafe_allow_html=True)

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": llm_response,
                    "tts_embed": tts_embed if voice_embed else "",
                }
            )

            st.session_state.autoplay_index = len(st.session_state.messages) - 1

    st.session_state.prompt_text = ""
    st.session_state.stt_processed = False
    st.rerun()