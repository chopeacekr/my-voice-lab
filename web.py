import os
import base64
from tempfile import NamedTemporaryFile

import streamlit as st
from audiorecorder import audiorecorder
from langchain_google_genai import ChatGoogleGenerativeAI

import torch
from TTS.api import TTS  # XTTS v2 (Coqui)

# 🔹 MeloTTS HTTP 클라이언트는 별도 모듈에서 import
from melotts_client import melotts_tts_http


# ================================
# 기본 설정
# ================================
os.environ.setdefault("MECABRC", "/var/lib/mecab/dic/debian/sys.dic")

device = "cuda" if torch.cuda.is_available() else "cpu"
print("device:", device)

# 녹음이 전혀 없을 때 사용할 기본 화자 (로컬 파일)
DEFAULT_SPEAKER_WAV = "my_voice1.wav"


# ================================
# 언어 설정
# ================================
SUPPORTED_LANGUAGES = {
    "Korean":  {"code": "ko", "llm": "Korean", "melo": "KR"},
    "English": {"code": "en", "llm": "English", "melo": "EN"},
    "Japanese": {"code": "en", "llm": "Japanese", "melo": "JP"},
    "French": {"code": "fr", "llm": "French", "melo": "FR"},
    "German": {"code": "de", "llm": "German", "melo": None},
    "Spanish": {"code": "es", "llm": "Spanish", "melo": "ES"},
    "Italian": {"code": "it", "llm": "Italian", "melo": None},
    "Portuguese": {"code": "pt", "llm": "Portuguese", "melo": None},
    "Polish": {"code": "pl", "llm": "Polish", "melo": None},
    "Turkish": {"code": "tr", "llm": "Turkish", "melo": None},
    "Russian": {"code": "ru", "llm": "Russian", "melo": None},
    "Dutch": {"code": "nl", "llm": "Dutch", "melo": None},
    "Chinese": {"code": "zh", "llm": "Chinese", "melo": "ZH"},
}


def language_names():
    return list(SUPPORTED_LANGUAGES.keys())


# ================================
# TTS 모델 레지스트리
# ================================
MODEL_REGISTRY = {
    "xtts_v2": {
        "label": "XTTS v2 (Coqui)",
        "model_id": "tts_models/multilingual/multi-dataset/xtts_v2",
        "type": "xtts_v2",
    },
    "melotts": {
        "label": "MeloTTS (Fast & Multilingual, via HTTP)",
        "model_id": None,
        "type": "melotts",
    },
}


def model_labels():
    return [cfg["label"] for cfg in MODEL_REGISTRY.values()]


def get_model_key_from_label(label: str) -> str:
    for key, cfg in MODEL_REGISTRY.items():
        if cfg["label"] == label:
            return key
    raise ValueError(f"Unknown model label: {label}")


# ================================
# 세션 상태 초기화
# ================================
if "messages" not in st.session_state:
    st.session_state.messages = []

if "speaker_path" not in st.session_state:
    st.session_state.speaker_path = DEFAULT_SPEAKER_WAV

# 기본 TTS 모델 선택
if "tts_model_key" not in st.session_state:
    st.session_state.tts_model_key = "xtts_v2"  # xtts_v2 | melotts

# 마지막 메시지 자동 재생 여부 (index)
if "autoplay_index" not in st.session_state:
    st.session_state.autoplay_index = None


# ================================
# XTTS 모델 로드 (페이지 라이프사이클 동안 1번만)
# ================================
original_torch_load = torch.load


def patched_torch_load(f, map_location=None, **kwargs):
    if map_location is None:
        map_location = "cpu"
    return original_torch_load(f, map_location=map_location, **kwargs)


@st.cache_resource
def get_xtts_model():
    """페이지 로딩 후, 처음 호출될 때 딱 한 번 로드"""
    cfg = MODEL_REGISTRY["xtts_v2"]
    torch.load = patched_torch_load
    try:
        model = TTS(cfg["model_id"]).to(device)
        print(f"Loaded XTTS model once: {cfg['model_id']}")
    finally:
        torch.load = original_torch_load
    return model


# ================================
# 오디오 HTML embed 유틸 (XTTS용)
# ================================
def embed_audio(file_path: str) -> str:
    with open(file_path, "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()

    html = f"""<audio controls>
    <source src="data:audio/wav;base64,{b64}" type="audio/wav">
    Your browser does not support the audio element.
</audio>"""
    return html


# ================================
# 공통 TTS inference
# ================================
def tts_inference(
    model_key: str,
    text: str,
    speaker_path: str | None,
    tts_model,
    lang_code: str,
    melo_lang_code: str = None,
) -> str:
    """
    model_key: "xtts_v2", "melotts" 등
    text: 생성할 텍스트
    speaker_path: 화자 reference 파일 (XTTS v2용, MeloTTS는 무시)
    tts_model: XTTS 모델 (melotts일 때는 None)
    lang_code: XTTS 언어 코드 ("ko", "en", ...)
    melo_lang_code: MeloTTS 언어 코드 ("KR", "EN", ...)
    """
    if text is None:
        return ""
    text = text.strip()
    if not text:
        return ""

    cfg = MODEL_REGISTRY[model_key]
    model_type = cfg["type"]

    # ---------- XTTS v2 ----------
    if model_type == "xtts_v2":
        if tts_model is None:
            print("⚠ XTTS model is not loaded, skipping TTS")
            return ""

        use_speaker = False
        if speaker_path and os.path.exists(speaker_path) and os.path.getsize(speaker_path) > 0:
            use_speaker = True
        else:
            print(f"⚠ speaker_wav 사용 안 함 (speaker_path={speaker_path})")

        out_path = "clone_output_xtts.wav"
        if use_speaker:
            print(f"👉 XTTS: speaker_wav 사용: {speaker_path}")
            tts_model.tts_to_file(
                text=text,
                file_path=out_path,
                speaker_wav=speaker_path,
                language=lang_code,
            )
        else:
            print("👉 XTTS: 기본 화자 사용 (no speaker_wav)")
            tts_model.tts_to_file(
                text=text,
                file_path=out_path,
                language=lang_code,
            )
        return embed_audio(out_path)

    # ---------- MeloTTS (HTTP) ----------
    elif model_type == "melotts":
        if not melo_lang_code:
            print("⚠ MeloTTS: melo_lang_code is None, skipping TTS")
            return ""

        print(f"👉 MeloTTS via HTTP: language={melo_lang_code}")
        speed = 1.0
        return melotts_tts_http(
            text=text,
            melo_lang_code=melo_lang_code,
            speed=speed,
            speaker=None,
        )

    print(f"⚠ Unsupported model type for inference: {model_type}")
    return ""


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
# Streamlit UI 시작
# ================================
st.title("Peace Chatbot System (Gemini + Multi-TTS)")

with st.sidebar:
    st.header("TTS Model")

    model_keys = list(MODEL_REGISTRY.keys())
    model_label_list = [MODEL_REGISTRY[k]["label"] for k in model_keys]
    try:
        default_index = model_keys.index(st.session_state.tts_model_key)
    except ValueError:
        default_index = model_keys.index("melotts")

    model_label = st.selectbox(
        "TTS Model",
        model_label_list,
        index=default_index,
    )
    model_key = get_model_key_from_label(model_label)
    st.session_state.tts_model_key = model_key

    st.header("Language")
    lang_display = st.selectbox("Language", language_names())
    lang_info = SUPPORTED_LANGUAGES[lang_display]
    lang_code = lang_info["code"]
    lang_for_llm = lang_info["llm"]
    melo_lang_code = lang_info.get("melo")

    if model_key == "melotts" and not melo_lang_code:
        st.warning(
            f"⚠️ MeloTTS does not support {lang_display}. "
            "Please select another language or use XTTS v2."
        )

    TTS_MODEL = get_xtts_model() if model_key == "xtts_v2" else None

    st.header("Control")
    gemini_api_key = st.text_input(
        "GEMINI API Key",
        key="chatbot_api_key",
        type="password",
    )

    # 🔹 LLM 요약 글자 수 설정
    llm_max_chars = st.number_input(
        "LLM 요약 최대 글자 수",
        min_value=50,
        max_value=1000,
        value=100,
        step=50,
    )

    voice_embed = st.toggle("Show Audio", value=True)
    btn_col1, btn_col2 = st.columns(2)
    with btn_col1:
        st.button("Rewind", on_click=rewind, use_container_width=True, type="primary")
    with btn_col2:
        st.button("Clear", on_click=clear_history, use_container_width=True)

    st.markdown("---")
    if model_key == "xtts_v2":
        st.write("현재 사용 중인 화자 레퍼런스:")
        st.code(st.session_state.speaker_path or "기본 화자 (my_voice1.wav)", language="bash")
    else:
        st.info("MeloTTS(HTTP)는 화자 레퍼런스를 사용하지 않습니다.")


# ================================
# 녹음 UI (항상 표시)
# ================================
st.subheader("Record your voice sample (for XTTS speaker reference)")

audio = audiorecorder("녹음시작", "녹음정지")

if len(audio) > 0:
    st.success("Recording complete!")
    with NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
        tmp_path = tmp_file.name
        audio.export(tmp_path, format="wav")
        st.write(f"저장된 파일: {tmp_path}")
        st.session_state.speaker_path = tmp_path

st.caption(
    "※ XTTS v2를 사용할 때 이 음성을 화자 레퍼런스로 사용합니다. "
    "MeloTTS를 사용할 때는 참고용으로만 저장됩니다."
)


# ================================
# 히스토리 표시 (autoplay는 마지막 assistant 메시지 한 번만)
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
if prompt := st.chat_input("Your message"):
    with st.chat_message("user"):
        st.markdown(prompt, unsafe_allow_html=True)

    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        with st.spinner("Generating response..."):
            if not gemini_api_key:
                st.error("GEMINI API Key를 먼저 입력해주세요.")
            else:
                if model_key == "melotts" and not melo_lang_code:
                    st.error(
                        f"MeloTTS does not support {lang_display}. "
                        "Please select another language or model."
                    )
                    llm_response = ""
                    tts_embed = ""
                else:
                    llm = ChatGoogleGenerativeAI(
                        model="gemini-2.5-flash",
                        temperature=0,
                        max_tokens=1024,
                        google_api_key=gemini_api_key,
                    )

                    raw_resp = llm.invoke(
                        prompt
                        + f"\nPlease answer in {lang_for_llm}, and keep it short, under {llm_max_chars} characters."
                    ).content

                    llm_response = (raw_resp or "").strip()

                    if not llm_response:
                        st.warning("LLM 응답이 비어 있어 TTS를 건너뜁니다.")
                        tts_embed = ""
                    else:
                        st.markdown(llm_response)
                        print("llm result: ", llm_response)
                        current_speaker = st.session_state.speaker_path

                        tts_embed = tts_inference(
                            model_key=st.session_state.tts_model_key,
                            text=llm_response,
                            speaker_path=current_speaker,
                            tts_model=TTS_MODEL,
                            lang_code=lang_code,
                            melo_lang_code=melo_lang_code,
                        )

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

    st.rerun()
