import base64
import re
import io
from tempfile import NamedTemporaryFile

import streamlit as st
from audiorecorder import audiorecorder
from langchain_google_genai import ChatGoogleGenerativeAI
from pydub import AudioSegment

# ⭐ 새 구조 Import
from api_clients.tts.gtts_client import gtts_tts
from api_clients.tts.melotts_client import melotts_tts_http
from api_clients.tts.xtts_v2_client import xtts_v2_tts_http
from api_clients.tts.bark_client import bark_tts_http, check_bark_health
from api_clients.tts.f5_client import f5_tts_http, check_f5_health

from api_clients.stt.gSR_client import google_sr_stt
from api_clients.stt.vosk_client import vosk_stt_http, check_vosk_health
from api_clients.stt.whisper_client import whisper_stt_http, check_whisper_health
from api_clients.stt.wav2vec2_client import wav2vec2_stt_http, check_wav2vec2_health

from api_clients.utils.audio_processor import preprocess_audio_for_stt, audio_segment_to_bytes
from api_clients.utils.audio_visualizer import (
    generate_waveform,
    generate_spectrogram,
    save_audio_with_visualizations
)


# ================================
# 언어 설정
# ================================
SUPPORTED_LANGUAGES = {
    "Korean":  {
        "code": "ko", 
        "llm": "Korean",
        "gtts": "ko",
        "melo": "KR", 
        "vosk": "KR", 
        "whisper": "KR", 
        "gsr": "ko-KR", 
        "wav2vec2": "KR", 
        "bark": "KR", 
        "f5": "KR"
    },
    "English": {
        "code": "en", 
        "llm": "English",
        "gtts": "en",
        "melo": "EN", 
        "vosk": "EN", 
        "whisper": "EN", 
        "gsr": "en-US", 
        "wav2vec2": "EN", 
        "bark": "EN", 
        "f5": "EN"
    },
    "Japanese": {
        "code": "ja", 
        "llm": "Japanese",
        "gtts": "ja",
        "melo": "JP", 
        "vosk": "JP", 
        "whisper": "JP", 
        "gsr": "ja-JP", 
        "wav2vec2": "JP", 
        "bark": "JP", 
        "f5": "JP"
    },
    "French": {
        "code": "fr", 
        "llm": "French",
        "gtts": "fr",
        "melo": "FR", 
        "vosk": "FR", 
        "whisper": "FR", 
        "gsr": "fr-FR", 
        "wav2vec2": "FR", 
        "bark": "FR", 
        "f5": "FR"
    },
    "German": {
        "code": "de", 
        "llm": "German",
        "gtts": "de",
        "melo": None, 
        "vosk": "DE", 
        "whisper": "DE", 
        "gsr": "de-DE", 
        "wav2vec2": "DE", 
        "bark": "DE", 
        "f5": "DE"
    },
    "Spanish": {
        "code": "es", 
        "llm": "Spanish",
        "gtts": "es",
        "melo": "ES", 
        "vosk": "ES", 
        "whisper": "ES", 
        "gsr": "es-ES", 
        "wav2vec2": "ES", 
        "bark": "ES", 
        "f5": "ES"
    },
    "Italian": {
        "code": "it", 
        "llm": "Italian",
        "gtts": "it",
        "melo": None, 
        "vosk": None, 
        "whisper": None, 
        "gsr": "it-IT", 
        "wav2vec2": None, 
        "bark": "IT", 
        "f5": "IT"
    },
    "Portuguese": {
        "code": "pt", 
        "llm": "Portuguese",
        "gtts": "pt",
        "melo": None, 
        "vosk": None, 
        "whisper": None, 
        "gsr": "pt-PT", 
        "wav2vec2": None, 
        "bark": "PT", 
        "f5": "PT"
    },
    "Polish": {
        "code": "pl", 
        "llm": "Polish",
        "gtts": "pl",
        "melo": None, 
        "vosk": None, 
        "whisper": None, 
        "gsr": "pl-PL", 
        "wav2vec2": None, 
        "bark": "PL", 
        "f5": None
    },
    "Turkish": {
        "code": "tr", 
        "llm": "Turkish",
        "gtts": "tr",
        "melo": None, 
        "vosk": None, 
        "whisper": None, 
        "gsr": "tr-TR", 
        "wav2vec2": None, 
        "bark": "TR", 
        "f5": None
    },
    "Russian": {
        "code": "ru", 
        "llm": "Russian",
        "gtts": "ru",
        "melo": None, 
        "vosk": "RU", 
        "whisper": "RU", 
        "gsr": "ru-RU", 
        "wav2vec2": "RU", 
        "bark": "RU", 
        "f5": None
    },
    "Dutch": {
        "code": "nl", 
        "llm": "Dutch",
        "gtts": "nl",
        "melo": None, 
        "vosk": None, 
        "whisper": None, 
        "gsr": "nl-NL", 
        "wav2vec2": None, 
        "bark": None, 
        "f5": None
    },
    "Chinese": {
        "code": "zh", 
        "llm": "Chinese",
        "gtts": "zh-CN",
        "melo": "ZH", 
        "vosk": "ZH", 
        "whisper": "ZH", 
        "gsr": "zh-CN", 
        "wav2vec2": "ZH", 
        "bark": "ZH", 
        "f5": "ZH"
    },
    "Hindi": {
        "code": "hi", 
        "llm": "Hindi",
        "gtts": "hi",
        "melo": None, 
        "vosk": None, 
        "whisper": None, 
        "gsr": "hi-IN", 
        "wav2vec2": None, 
        "bark": "HI", 
        "f5": None
    },
}


def language_names():
    return list(SUPPORTED_LANGUAGES.keys())


# ================================
# TTS 모델 레지스트리
# ================================
TTS_MODEL_REGISTRY = {
    "gtts": {
        "label": "gTTS (Google TTS - Free)",
        "type": "gtts",
        "description": "무료 Google TTS (0.5-1초, 서버 불필요)",
        "features": ["무료", "서버 불필요", "빠름", "인터넷 필요"],
    },
    "melotts": {
        "label": "MeloTTS (Fast & Multilingual)",
        "type": "melotts",
        "description": "빠른 다국어 음성 합성 (1-2초)",
        "features": ["빠른 처리", "다국어", "서버 필요"],
    },
    "xtts_v2": {
        "label": "XTTS v2 (Voice Cloning)",
        "type": "xtts_v2",
        "description": "고품질 Voice Cloning (5-10초)",
        "features": ["Voice Cloning", "고품질", "서버 필요"],
    },
    "f5_tts": {
        "label": "F5-TTS (Zero-shot Voice Cloning)",
        "type": "f5_tts",
        "description": "최고 품질 Zero-shot Voice Cloning (10-20초)",
        "features": ["Zero-shot", "최고 품질", "자연스러움", "서버 필요"],
    },
    "bark": {
        "label": "Bark (Expressive & Emotional)",
        "type": "bark",
        "description": "표현력 높은 감정 음성 합성 (100-200초)",
        "features": ["감정 표현", "음악/효과음", "100+ 화자", "서버 필요"],
    },
}


# ================================
# STT 모델 레지스트리
# ================================
STT_MODEL_REGISTRY = {
    "google_sr": {
        "label": "Google SR (Cloud STT - Free)",
        "type": "google_sr",
    },
    "whisper": {
        "label": "Whisper (Accurate STT)",
        "type": "whisper",
    },
    "wav2vec2": {
        "label": "Wav2Vec2 (Korean Optimized)",
        "type": "wav2vec2",
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
    st.session_state.tts_model_key = "gtts"

if "stt_model_key" not in st.session_state:
    st.session_state.stt_model_key = "google_sr"

if "experimental_mode" not in st.session_state:
    st.session_state.experimental_mode = False

if "bark_voice_preset" not in st.session_state:
    st.session_state.bark_voice_preset = None

if "bark_speed" not in st.session_state:
    st.session_state.bark_speed = 1.0

if "f5_ref_audio_path" not in st.session_state:
    st.session_state.f5_ref_audio_path = "my_voice1.wav"

if "f5_ref_text" not in st.session_state:
    st.session_state.f5_ref_text = ""

if "f5_use_reference" not in st.session_state:
    st.session_state.f5_use_reference = True

if "autoplay_index" not in st.session_state:
    st.session_state.autoplay_index = None

if "prompt_text" not in st.session_state:
    st.session_state.prompt_text = ""

if "stt_processed" not in st.session_state:
    st.session_state.stt_processed = False

if "recorder_key_counter" not in st.session_state:
    st.session_state.recorder_key_counter = 0

if "tts_model_label" not in st.session_state:
    st.session_state.tts_model_label = TTS_MODEL_REGISTRY["gtts"]["label"]

if "stt_model_label" not in st.session_state:
    st.session_state.stt_model_label = STT_MODEL_REGISTRY["google_sr"]["label"]

# 그래프 표시 여부를 메시지별로 기억
if "show_graphs" not in st.session_state:
    st.session_state.show_graphs = {}


# ================================
# TTS inference
# ================================
def tts_inference(
    model_key: str,
    text: str | None,
    speaker_path: str | None,
    lang_code: str,
    gtts_lang_code: str | None = None,
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

    if model_type == "gtts":
        if not gtts_lang_code:
            print("⚠ gTTS: gtts_lang_code is None, using default 'ko'")
            gtts_lang_code = "ko"
        print(f"👉 gTTS: language={gtts_lang_code}")
        return gtts_tts(
            text=text,
            lang_code=gtts_lang_code,
        )

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

    if model_type == "xtts_v2":
        print(f"👉 XTTS v2 via HTTP: language={lang_code}")
        return xtts_v2_tts_http(
            text=text,
            lang_code=lang_code,
            speaker_wav_path=speaker_path,
            speed=1.0,
        )

    if model_type == "f5_tts":
        if not f5_lang_code:
            print("⚠ F5-TTS: f5_lang_code is None, using default")
        
        if not f5_ref_audio_path:
            f5_ref_audio_path = "my_voice1.wav"
            print("⚠ F5-TTS: ref_audio is None, using default (my_voice1.wav)")
        
        print(f"👉 F5-TTS via HTTP: language={f5_lang_code}, ref_audio={f5_ref_audio_path}, ref_text={f5_ref_text}")
        return f5_tts_http(
            text=text,
            ref_audio_path=f5_ref_audio_path,
            ref_text=f5_ref_text,
        )

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
    cfg = STT_MODEL_REGISTRY[model_key]
    model_type = cfg["type"]

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
    st.session_state.autoplay_index = None
    st.session_state.show_graphs = {}


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
    st.header("🧪 Experimental")
    st.session_state.experimental_mode = st.toggle(
        "Experimental Mode",
        value=st.session_state.experimental_mode,
        help="Enable audio visualization & ZIP download"
    )
    
    if st.session_state.experimental_mode:
        st.success("✅ Audio visualization enabled")
        st.caption("• 녹음 재생 플레이어\n• [저장] 버튼 (ZIP)\n• Waveform/Spectrogram")
    else:
        st.info("ℹ️ Audio visualization disabled")
    
    st.markdown("---")
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
    st.session_state.tts_model_label = tts_model_label  # ⭐ 사이드바에서 선택된 라벨 저장

    tts_cfg = TTS_MODEL_REGISTRY[tts_model_key]
    st.caption(f"📝 {tts_cfg['description']}")
    st.caption(f"✨ {', '.join(tts_cfg['features'])}")

    if tts_model_key == "gtts":
        st.success("✅ gTTS Ready (No server required)")
        st.caption("📡 Internet connection required")

    elif tts_model_key == "f5_tts":
        st.markdown("---")
        st.subheader("🎤 F5-TTS 옵션")
        
        st.info("💡 F5-TTS는 참조 음성이 필수입니다. 기본: my_voice1.wav")
        
        st.session_state.f5_use_reference = st.checkbox(
            "참조 음성 사용",
            value=st.session_state.f5_use_reference,
            help="F5-TTS는 항상 참조 음성을 사용합니다"
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
            else:
                st.error("❌ F5-TTS Server Error")
        except:
            st.error("❌ F5-TTS Server Offline")

    elif tts_model_key == "bark":
        st.markdown("---")
        st.subheader("🐶 Bark 옵션")
        
        st.warning("⚠️ Bark는 처리 시간이 매우 깁니다 (100-200초)")
        
        voice_preset_options = {
            "기본 (자동)": None,
            "영어-남성1": "v2/en_speaker_0",
            "영어-여성1": "v2/en_speaker_1",
            "한국어-남성1": "v2/ko_speaker_0",
            "한국어-여성1": "v2/ko_speaker_1",
            "중국어-남성1": "v2/zh_speaker_0",
        }
        
        voice_preset_display = st.selectbox(
            "화자 프리셋",
            options=list(voice_preset_options.keys()),
        )
        st.session_state.bark_voice_preset = voice_preset_options[voice_preset_display]
        
        st.session_state.bark_speed = st.slider(
            "음성 속도",
            min_value=0.5,
            max_value=2.0,
            value=1.0,
            step=0.1,
        )
        
        try:
            health = check_bark_health()
            if health.get("status") == "ok":
                st.success("✅ Bark Server Connected (Port 8600)")
            else:
                st.error("❌ Bark Server Error")
        except:
            st.error("❌ Bark Server Offline")

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
    st.session_state.stt_model_key = stt_model_key
    st.session_state.stt_model_label = stt_model_label  # ⭐ 사이드바에서 선택된 라벨 저장

    if stt_model_key == "google_sr":
        st.success("✅ Google SR Ready (No server required)")
        st.caption("📡 Internet connection required")
    
    elif stt_model_key == "vosk":
        try:
            health = check_vosk_health()
            if health.get("status") == "ok":
                st.success("✅ Vosk STT Server Connected")
            else:
                st.error("❌ Vosk STT Server Error")
        except:
            st.error("❌ Vosk STT Server Offline")
    
    elif stt_model_key == "whisper":
        try:
            health = check_whisper_health()
            if health.get("status") == "ok":
                st.success("✅ Whisper STT Server Connected")
            else:
                st.error("❌ Whisper STT Server Error")
        except:
            st.error("❌ Whisper STT Server Offline")
    
    elif stt_model_key == "wav2vec2":
        try:
            health = check_wav2vec2_health()
            if health.get("status") == "ok":
                st.success("✅ Wav2Vec2 STT Server Connected")
            else:
                st.error("❌ Wav2Vec2 STT Server Error")
        except:
            st.error("❌ Wav2Vec2 STT Server Offline")

    st.markdown("---")
    st.header("🌍 Language")
    lang_display = st.selectbox("Language", language_names())
    lang_info = SUPPORTED_LANGUAGES[lang_display]
    lang_code = lang_info["code"]
    lang_for_llm = lang_info["llm"]
    gtts_lang_code = lang_info.get("gtts")
    melo_lang_code = lang_info.get("melo")
    vosk_lang_code = lang_info.get("vosk")
    whisper_lang_code = lang_info.get("whisper")
    gsr_lang_code = lang_info.get("gsr")
    wav2vec2_lang_code = lang_info.get("wav2vec2")
    bark_lang_code = lang_info.get("bark")
    f5_lang_code = lang_info.get("f5")

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


# ================================
# 참조 음성 녹음
# ================================
st.subheader("🎤 Record your voice sample")

audio = audiorecorder("녹음시작", "녹음정지", key="voice_recorder")

if len(audio) > 0:
    st.success("Recording complete!")
    with NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
        tmp_path = tmp_file.name
        audio.export(tmp_path, format="wav")
        st.session_state.speaker_path = tmp_path
        
        if st.session_state.tts_model_key == "f5_tts":
            st.session_state.f5_ref_audio_path = tmp_path
            st.info("💡 F5-TTS 참조 음성으로 설정되었습니다.")
    
    if st.session_state.experimental_mode:
        st.markdown("---")
        st.subheader("🎧 Recorded Audio Playback")
        
        audio_bytes = audio_segment_to_bytes(audio)
        audio_b64 = base64.b64encode(audio_bytes).decode('utf-8')
        audio_html = f'<audio controls><source src="data:audio/wav;base64,{audio_b64}" type="audio/wav"></audio>'
        
        st.markdown(audio_html, unsafe_allow_html=True)
        
        # 저장 & 그래프 (동시 표시)
        save_btn_key = f"save_rec_{st.session_state.recorder_key_counter}"
        if st.button("💾 저장&그래프 보기", key=save_btn_key, use_container_width=True):
            with st.spinner("Creating ZIP & Generating graphs..."):
                zip_bytes, zip_filename = save_audio_with_visualizations(
                    audio_bytes, 
                    filename_prefix="recorded"
                )
                
                if zip_bytes:
                    st.download_button(
                        label=f"📥 다운로드: {zip_filename}",
                        data=zip_bytes,
                        file_name=zip_filename,
                        mime="application/zip",
                        key=f"dl_{save_btn_key}",
                        use_container_width=True
                    )
                    st.success("✅ ZIP 생성 완료!")
                    
                    # 자동으로 그래프 표시
                    col_wave, col_spec = st.columns(2)
                    
                    with col_wave:
                        st.caption("Waveform")
                        waveform_bytes = generate_waveform(audio_bytes)
                        if waveform_bytes:
                            st.image(waveform_bytes, use_column_width=True)
                    
                    with col_spec:
                        st.caption("Spectrogram")
                        spectrogram_bytes = generate_spectrogram(audio_bytes)
                        if spectrogram_bytes:
                            st.image(spectrogram_bytes, use_column_width=True)


# ================================
# 채팅 히스토리 렌더링
# ================================
autoplay_index = st.session_state.autoplay_index

for i, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        msg_type = msg.get("type")
        
        # -------------------------
        # STT 전용 메시지 표시
        # -------------------------
        if msg_type == "stt":
            model_label = msg.get("stt_model_label") or st.session_state.stt_model_label
            st.markdown(f"**STT 모델명:** {model_label}")
            st.markdown("**STT 입력(음성):**")
            audio_b64 = msg.get("audio_b64")
            
            if voice_embed and audio_b64:
                autoplay_attr = ""  # STT 입력은 자동 재생 X
                audio_html = (
                    f'<audio controls{autoplay_attr}>'
                    f'<source src="data:audio/wav;base64,{audio_b64}" type="audio/wav"></audio>'
                )
                st.markdown(audio_html, unsafe_allow_html=True)

            # 실험 모드에서 저장&그래프 버튼
            if st.session_state.experimental_mode and audio_b64:
                audio_bytes = base64.b64decode(audio_b64)
                state_key = f"stt_{i}"
                already_show = st.session_state.show_graphs.get(state_key, False)
                
                if st.button("💾 저장&그래프 보기", key=f"btn_graph_{state_key}") or already_show:
                    st.session_state.show_graphs[state_key] = True
                    with st.spinner("Creating ZIP & Generating graphs..."):
                        zip_bytes, zip_filename = save_audio_with_visualizations(
                            audio_bytes,
                            filename_prefix="stt_input"
                        )
                        if zip_bytes:
                            st.download_button(
                                label=f"📥 다운로드: {zip_filename}",
                                data=zip_bytes,
                                file_name=zip_filename,
                                mime="application/zip",
                                key=f"dl_{state_key}",
                                use_container_width=True
                            )
                            st.success("✅ ZIP 생성 완료!")
                    
                    col_wave, col_spec = st.columns(2)
                    with col_wave:
                        st.caption("Waveform")
                        waveform_bytes = generate_waveform(audio_bytes)
                        if waveform_bytes:
                            st.image(waveform_bytes, use_column_width=True)
                    with col_spec:
                        st.caption("Spectrogram")
                        spectrogram_bytes = generate_spectrogram(audio_bytes)
                        if spectrogram_bytes:
                            st.image(spectrogram_bytes, use_column_width=True)

            st.markdown(f"**STT 결과(텍스트):** {msg.get('stt_text', '')}")

        # -------------------------
        # TTS 출력 메시지 (TTS Only / LLM+TTS)
        # -------------------------
        elif msg_type in ("tts_only", "llm_tts"):
            tts_input_text = msg.get("tts_input_text", msg.get("content", ""))
            model_label = msg.get("tts_model_label") or st.session_state.tts_model_label
            st.markdown(f"**TTS 모델명:** {model_label}")
            st.markdown(f"**TTS 입력(Text):** {tts_input_text}")
            
            audio_b64 = msg.get("audio_b64") or msg.get("audio_bytes")
            if voice_embed and audio_b64:
                autoplay_attr = ""
                if autoplay_index is not None and i == autoplay_index:
                    autoplay_attr = " autoplay"
                audio_html = (
                    f'<audio controls{autoplay_attr}>'
                    f'<source src="data:audio/wav;base64,{audio_b64}" type="audio/wav"></audio>'
                )
                st.markdown("**TTS 출력(음성):**")
                st.markdown(audio_html, unsafe_allow_html=True)

            # 실험 모드: 저장&그래프 버튼
            if st.session_state.experimental_mode and audio_b64:
                audio_bytes = base64.b64decode(audio_b64)
                state_key = f"tts_{i}"
                already_show = st.session_state.show_graphs.get(state_key, False)
                
                if st.button("💾 저장&그래프 보기", key=f"btn_graph_{state_key}") or already_show:
                    st.session_state.show_graphs[state_key] = True
                    with st.spinner("Creating ZIP & Generating graphs..."):
                        zip_bytes, zip_filename = save_audio_with_visualizations(
                            audio_bytes,
                            filename_prefix="tts_output"
                        )
                        if zip_bytes:
                            st.download_button(
                                label=f"📥 다운로드: {zip_filename}",
                                data=zip_bytes,
                                file_name=zip_filename,
                                mime="application/zip",
                                key=f"dl_{state_key}",
                                use_container_width=True
                            )
                            st.success("✅ ZIP 생성 완료!")
                    
                    col_wave, col_spec = st.columns(2)
                    with col_wave:
                        st.caption("Waveform")
                        waveform_bytes = generate_waveform(audio_bytes)
                        if waveform_bytes:
                            st.image(waveform_bytes, use_column_width=True)
                    with col_spec:
                        st.caption("Spectrogram")
                        spectrogram_bytes = generate_spectrogram(audio_bytes)
                        if spectrogram_bytes:
                            st.image(spectrogram_bytes, use_column_width=True)

        # -------------------------
        # 일반 텍스트 메시지 (기존 호환용)
        # -------------------------
        else:
            content = msg.get("content", "")
            if voice_embed:
                # 기존 구조 호환용
                embed = msg.get("tts_embed", "")
                if embed and autoplay_index is not None and i == autoplay_index:
                    embed = embed.replace("<audio controls>", "<audio controls autoplay>")
                if embed:
                    content = "\n\n".join([content, embed])
                
                audio_embed = msg.get("audio_embed", "")
                if audio_embed:
                    content = "\n\n".join([content, audio_embed])
            
            if content:
                st.markdown(content, unsafe_allow_html=True)

st.session_state.autoplay_index = None


# ================================
# 채팅 입력부
# ================================
st.subheader("💬 Chat Input")

col1, col2 = st.columns([5, 1])

with col2:
    stt_available = False
    
    if st.session_state.stt_model_key == "vosk" and vosk_lang_code:
        stt_available = True
    elif st.session_state.stt_model_key == "whisper" and whisper_lang_code:
        stt_available = True
    elif st.session_state.stt_model_key == "google_sr" and gsr_lang_code:
        stt_available = True
    elif st.session_state.stt_model_key == "wav2vec2" and wav2vec2_lang_code:
        stt_available = True
    
    if stt_available:
        audio_stt = audiorecorder("🎤", "⏹️", key=f"stt_{st.session_state.recorder_key_counter}")
    else:
        audio_stt = None
        st.caption("STT 미지원")

# 새 녹음이 없으면 플래그 리셋
if not audio_stt or len(audio_stt) == 0:
    st.session_state.stt_processed = False

prompt = None

# ================================
# STT 처리 (녹음 정지 시)
# ================================
if audio_stt and len(audio_stt) > 0 and not st.session_state.stt_processed:
    st.session_state.stt_processed = True  # 중복 처리 방지
    
    with st.spinner("Converting..."):
        try:
            audio_bytes = preprocess_audio_for_stt(audio_stt)
            
            transcribed_text = stt_inference(
                model_key=st.session_state.stt_model_key,
                audio_bytes=audio_bytes,
                vosk_lang_code=vosk_lang_code,
                whisper_lang_code=whisper_lang_code,
                gsr_lang_code=gsr_lang_code,
                wav2vec2_lang_code=wav2vec2_lang_code,
            )
            
            if transcribed_text.strip():
                # 텍스트 입력창에 설정
                st.session_state.prompt_text = transcribed_text.strip()
                
                # STT 입력을 채팅 메시지로 저장 (항상)
                audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
                st.session_state.messages.append({
                    "role": "user",
                    "type": "stt",
                    "stt_text": transcribed_text.strip(),
                    "audio_b64": audio_b64,
                    "stt_model_label": st.session_state.stt_model_label,  # ⭐ 사용 당시 모델 라벨 저장
                })
                
                st.success(f"✅ 인식: {transcribed_text}")
                st.info("💡 아래 Send 버튼을 눌러 AI에게 전송하세요.")
            else:
                st.warning("⚠️ 음성이 인식되지 않았습니다.")
                
        except Exception as e:
            st.error(f"❌ STT 실패: {e}")
        
        finally:
            st.session_state.recorder_key_counter += 1
            st.rerun()


with col1:
    prompt_text = st.text_area(
        "Your message",
        value=st.session_state.prompt_text,
        height=80,
    )
    
    if prompt_text != st.session_state.prompt_text:
        st.session_state.prompt_text = prompt_text

col_send1, col_send2 = st.columns([1, 1])
with col_send1:
    send_clicked = st.button("Send (LLM + TTS)", type="primary", use_container_width=True)
with col_send2:
    tts_only_clicked = st.button("🔊 TTS Only", use_container_width=True)


# ================================
# TTS Only 처리
# ================================
if tts_only_clicked and st.session_state.prompt_text:
    test_text = st.session_state.prompt_text.strip()
    
    with st.spinner("🎤 음성 생성 중..."):
        try:
            tts_embed = tts_inference(
                model_key=st.session_state.tts_model_key,
                text=test_text,
                speaker_path=st.session_state.speaker_path,
                lang_code=lang_code,
                gtts_lang_code=gtts_lang_code,
                melo_lang_code=melo_lang_code,
                bark_lang_code=bark_lang_code,
                bark_voice_preset=st.session_state.bark_voice_preset,
                bark_speed=st.session_state.bark_speed,
                f5_lang_code=f5_lang_code,
                f5_ref_audio_path=st.session_state.f5_ref_audio_path if st.session_state.f5_use_reference else "my_voice1.wav",
                f5_ref_text=st.session_state.f5_ref_text if st.session_state.f5_use_reference else None,
            )
        except Exception as e:
            st.error(f"⚠️ TTS 실패: {e}")
            tts_embed = ""
    
    audio_b64 = None
    if tts_embed:
        match = re.search(r'base64,([A-Za-z0-9+/=]+)', tts_embed)
        if match:
            audio_b64 = match.group(1)
    
    if audio_b64:
        st.session_state.messages.append({
            "role": "assistant",
            "type": "tts_only",
            "tts_input_text": test_text,
            "audio_b64": audio_b64,
            "tts_model_label": st.session_state.tts_model_label,  # ⭐ 사용 당시 모델 라벨 저장
        })
        st.session_state.autoplay_index = len(st.session_state.messages) - 1
    
    st.rerun()


# ================================
# Send (LLM + TTS) 처리
# ================================
if send_clicked and st.session_state.prompt_text:
    prompt = st.session_state.prompt_text.strip()

    # 사용자 텍스트 메시지 저장
    st.session_state.messages.append({"role": "user", "content": prompt})

    llm_response = ""
    tts_embed = ""

    with st.spinner("Generating..."):
        if not gemini_api_key:
            st.error("GEMINI API Key를 먼저 입력해주세요.")
        else:
            try:
                llm = ChatGoogleGenerativeAI(
                    model="gemini-2.5-flash",
                    temperature=0,
                    max_tokens=1024,
                    google_api_key=gemini_api_key,
                )
                
                raw_resp = llm.invoke(
                    prompt + f"\nPlease answer in {lang_for_llm}, under {llm_max_chars} characters."
                ).content
                
                llm_response = (raw_resp or "").strip()
                
                if llm_response:
                    tts_embed = tts_inference(
                        model_key=st.session_state.tts_model_key,
                        text=llm_response,
                        speaker_path=st.session_state.speaker_path,
                        lang_code=lang_code,
                        gtts_lang_code=gtts_lang_code,
                        melo_lang_code=melo_lang_code,
                        bark_lang_code=bark_lang_code,
                        bark_voice_preset=st.session_state.bark_voice_preset,
                        bark_speed=st.session_state.bark_speed,
                        f5_lang_code=f5_lang_code,
                        f5_ref_audio_path=st.session_state.f5_ref_audio_path if st.session_state.f5_use_reference else "my_voice1.wav",
                        f5_ref_text=st.session_state.f5_ref_text if st.session_state.f5_use_reference else None,
                    )
            except Exception as e:
                st.error(f"❌ 오류: {e}")
                llm_response = ""
                tts_embed = ""

    audio_b64 = None
    if tts_embed:
        match = re.search(r'base64,([A-Za-z0-9+/=]+)', tts_embed)
        if match:
            audio_b64 = match.group(1)

    # LLM + TTS 메시지를 하나의 레코드로 저장
    st.session_state.messages.append({
        "role": "assistant",
        "type": "llm_tts",
        "content": llm_response,
        "tts_input_text": llm_response,
        "audio_b64": audio_b64,
        "tts_model_label": st.session_state.tts_model_label,  # ⭐ 사용 당시 모델 라벨 저장
    })

    st.session_state.autoplay_index = len(st.session_state.messages) - 1

    # 입력 리셋 & STT 플래그 리셋
    st.session_state.prompt_text = ""
    st.session_state.stt_processed = False
    st.rerun()
