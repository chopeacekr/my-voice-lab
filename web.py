import os
import base64
from tempfile import NamedTemporaryFile

import streamlit as st
from audiorecorder import audiorecorder
from langchain_google_genai import ChatGoogleGenerativeAI

import torch
from TTS.api import TTS


# ================================
# 기본 설정
# ================================
device = "cuda" if torch.cuda.is_available() else "cpu"
print("device:", device)

# 녹음이 전혀 없을 때 사용할 기본 화자 (로컬 파일)
# web.py와 같은 폴더에 my_voice1.wav 를 두세요.
DEFAULT_SPEAKER_WAV = "my_voice1.wav"


# ================================
# 언어 설정 (나중에 모델이 바뀌어도 공통 사용)
# ================================
# 표시 이름 -> XTTS 언어 코드 + LLM용 언어 이름
SUPPORTED_LANGUAGES = {
    "Korean":  {"code": "ko", "llm": "Korean"},
    "English": {"code": "en", "llm": "English"},
    "Japanese": {"code": "ja", "llm": "Japanese"},
    "French": {"code": "fr", "llm": "French"},
    "German": {"code": "de", "llm": "German"},
    "Spanish": {"code": "es", "llm": "Spanish"},
    "Italian": {"code": "it", "llm": "Italian"},
    "Portuguese": {"code": "pt", "llm": "Portuguese"},
    "Polish": {"code": "pl", "llm": "Polish"},
    "Turkish": {"code": "tr", "llm": "Turkish"},
    "Russian": {"code": "ru", "llm": "Russian"},
    "Dutch": {"code": "nl", "llm": "Dutch"},
}


def language_names():
    return list(SUPPORTED_LANGUAGES.keys())


# ================================
# TTS 모델 레지스트리 (새 모델 추가 용이하게)
# ================================
MODEL_REGISTRY = {
    "xtts_v2": {
        "label": "XTTS v2 (Coqui)",
        "model_id": "tts_models/multilingual/multi-dataset/xtts_v2",
        "type": "xtts_v2",  # tts_inference 분기용
    },
    # 나중에 다른 모델 추가 시 여기만 추가하면 됨
    # 예:
    # "another_model": {
    #     "label": "My Other TTS",
    #     "model_id": "some/model/name",
    #     "type": "xtts_v2",  # 또는 새로운 타입 정의
    # },
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

if "tts_model_key" not in st.session_state:
    # 기본은 xtts_v2
    st.session_state.tts_model_key = "xtts_v2"


# ================================
# Torch load patch (XTTS 로딩 버그 회피용)
# ================================
original_torch_load = torch.load


def patched_torch_load(f, map_location=None, **kwargs):
    if map_location is None:
        map_location = "cpu"
    return original_torch_load(f, map_location=map_location, **kwargs)


# ================================
# TTS 모델 로딩 (모델 종류에 따라 분기)
# ================================
@st.cache_resource
def load_tts_model(model_key: str):
    """
    model_key: "xtts_v2", ...
    """
    cfg = MODEL_REGISTRY[model_key]
    model_type = cfg["type"]

    if model_type == "xtts_v2":
        # XTTS v2는 torch.load 패치가 필요할 수 있음
        torch.load = patched_torch_load
        try:
            tts_model = TTS(cfg["model_id"]).to(device)
            print(f"Loaded XTTS model: {cfg['model_id']}")
        finally:
            torch.load = original_torch_load
        return tts_model

    # 나중에 다른 타입 추가 가능
    raise ValueError(f"Unsupported model type: {model_type}")


# ================================
# 오디오 HTML embed 유틸
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
# (현재는 XTTS v2만 구현, 나중에 type별로 확장)
# ================================
def tts_inference(
    model_key: str,
    text: str,
    speaker_path: str | None,
    tts_model,
    lang_code: str,
) -> str:
    """
    model_key: "xtts_v2" 등
    text: 생성할 텍스트
    speaker_path: 화자 reference 파일 (없으면 기본화자)
    tts_model: load_tts_model()로 받은 인스턴스
    lang_code: XTTS 언어 코드 ("ko", "en", ...)
    """
    if not text or not text.strip():
        raise ValueError("TTS에 사용할 text가 비어 있습니다.")

    use_speaker = False
    if speaker_path and os.path.exists(speaker_path) and os.path.getsize(speaker_path) > 0:
        use_speaker = True
    else:
        print(f"⚠ speaker_wav 사용 안 함 (speaker_path={speaker_path})")

    cfg = MODEL_REGISTRY[model_key]
    model_type = cfg["type"]

    # ---------- XTTS v2 ----------
    if model_type == "xtts_v2":
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

    # ---------- 나중에 다른 타입 추가 시 여기 분기 ----------
    raise ValueError(f"Unsupported model type for inference: {model_type}")


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
st.title("Peace Chatbot System (Gemini + XTTS v2)")

with st.sidebar:
    st.header("TTS Model")

    model_label = st.selectbox(
        "TTS Model",
        [cfg["label"] for cfg in MODEL_REGISTRY.values()],
    )
    model_key = get_model_key_from_label(model_label)
    st.session_state.tts_model_key = model_key

    st.header("Language")
    lang_display = st.selectbox("Language", language_names())
    lang_info = SUPPORTED_LANGUAGES[lang_display]
    lang_code = lang_info["code"]
    lang_for_llm = lang_info["llm"]

    TTS_MODEL = load_tts_model(model_key)

    st.header("Control")
    gemini_api_key = st.text_input(
        "GEMINI API Key",
        key="chatbot_api_key",
        type="password",
    )
    voice_embed = st.toggle("Show Audio", value=True)
    btn_col1, btn_col2 = st.columns(2)
    with btn_col1:
        st.button("Rewind", on_click=rewind, use_container_width=True, type="primary")
    with btn_col2:
        st.button("Clear", on_click=clear_history, use_container_width=True)

    st.markdown("---")
    st.write("현재 사용 중인 화자 레퍼런스:")
    st.code(st.session_state.speaker_path or "기본 화자 (my_voice1.wav)", language="bash")


# ================================
# 녹음 UI
# ================================
st.subheader("Record your voice message")

audio = audiorecorder("녹음시작", "녹음정지")

# 새 녹음이 있으면 화자 레퍼런스를 그걸로 교체
if len(audio) > 0:
    st.success("Recording complete!")
    with NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
        tmp_path = tmp_file.name
        audio.export(tmp_path, format="wav")
        st.write(f"저장된 파일: {tmp_path}")
        st.session_state.speaker_path = tmp_path


# ================================
# 히스토리 표시
# ================================
for i, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        content = msg.get("content", "")
        if voice_embed:
            embed = msg.get("tts_embed", "")
            if i == len(st.session_state.messages) - 1:
                embed = embed.replace("<audio controls>", "<audio controls autoplay>")
            if embed:
                content = "\n\n".join([content, embed])
        st.markdown(content, unsafe_allow_html=True)


# ================================
# 채팅 입력 처리
# ================================
if prompt := st.chat_input("Your message"):
    with st.chat_message("user"):
        st.markdown(prompt, unsafe_allow_html=True)

    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        with st.spinner("Gemini & XTTS generating..."):
            if not gemini_api_key:
                st.error("GEMINI API Key를 먼저 입력해주세요.")
            else:
                llm = ChatGoogleGenerativeAI(
                    model="gemini-2.5-flash",
                    temperature=0,
                    max_tokens=1024,
                    google_api_key=gemini_api_key,
                )

                llm_response = llm.invoke(
                    prompt
                    + f"\nPlease answer in {lang_for_llm}, and keep it short, under 300 characters."
                ).content

                st.markdown(llm_response)
                print("llm result: ", llm_response)
                current_speaker = st.session_state.speaker_path

                tts_embed = tts_inference(
                    model_key=st.session_state.tts_model_key,
                    text=llm_response,
                    speaker_path=current_speaker,
                    tts_model=TTS_MODEL,
                    lang_code=lang_code,
                )

                st.markdown(tts_embed, unsafe_allow_html=True)

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": llm_response,
                        "tts_embed": tts_embed,
                    }
                )

    st.rerun()
