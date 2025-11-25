import os
import base64
from tempfile import NamedTemporaryFile
from io import BytesIO

import streamlit as st
from audiorecorder import audiorecorder
from langchain_google_genai import ChatGoogleGenerativeAI

import torch
from TTS.api import TTS


# -----------------------------
# GPU / Device 설정
# -----------------------------
device = "cuda" if torch.cuda.is_available() else "cpu"
print("device:", device)

# 앱 시작 시 사용할 기본 화자 reference 파일 (로컬에 준비해두기)
DEFAULT_SPEAKER_WAV = "my_voice1.wav"  # web.py와 같은 폴더에 있다고 가정


# -----------------------------
# 언어 설정
# -----------------------------
# 표시 이름 -> (XTTS 언어 코드, LLM에게 말할 언어 이름)
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
    # 중국어는 XTTS가 비정식 지원이긴 해서 필요하면 추가 가능
    # "Chinese": {"code": "zh", "llm": "Chinese"},
}


def language_names():
    """드롭다운에 표시할 언어 이름 리스트."""
    return list(SUPPORTED_LANGUAGES.keys())


# -----------------------------
# 세션 상태 초기화
# -----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "speaker_path" not in st.session_state:
    # 앱 처음 시작 시, 기본 화자를 my_voice1.wav로 설정
    st.session_state.speaker_path = DEFAULT_SPEAKER_WAV


# -----------------------------
# Torch load patch (XTTS 로딩 버그 회피용)
# -----------------------------
original_torch_load = torch.load


def patched_torch_load(f, map_location=None, **kwargs):
    if map_location is None:
        map_location = "cpu"
    return original_torch_load(f, map_location=map_location, **kwargs)


torch.load = patched_torch_load


# -----------------------------
# XTTS 모델 로딩 (캐시)
# -----------------------------
@st.cache_resource
def load_model():
    try:
        tts_model = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)
        print("XTTS v2 loaded")
        torch.load = original_torch_load  # 패치 되돌리기
    except Exception as e:
        print(f"Error loading XTTS model: {e}")
        raise
    return tts_model


# -----------------------------
# 유틸: 오디오 파일을 HTML audio 태그로 embed
# -----------------------------
def embed_audio(file_path: str) -> str:
    with open(file_path, "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()

    html = f"""<audio controls>
    <source src="data:audio/wav;base64,{b64}" type="audio/wav">
    Your browser does not support the audio element.
</audio>"""
    return html


# -----------------------------
# TTS Inference 함수
# -----------------------------
def tts_inference(text: str, speaker_path: str | None, tts_model: TTS, lang_code: str) -> str:
    """
    text: 생성할 텍스트
    speaker_path: 화자 reference wav/mp3 경로 (없으면 기본 화자)
    tts_model: XTTS 모델
    lang_code: "ko", "en" 등 XTTS 언어 코드
    """
    if not text or not text.strip():
        raise ValueError("TTS에 사용할 text가 비어 있습니다.")

    out_path = "clone_output.wav"

    use_speaker = False
    if speaker_path and os.path.exists(speaker_path) and os.path.getsize(speaker_path) > 0:
        use_speaker = True
    else:
        print(f"⚠ speaker_wav 사용 안 함 (speaker_path={speaker_path})")

    if use_speaker:
        print(f"👉 speaker_wav 사용: {speaker_path}")
        tts_model.tts_to_file(
            text=text,
            file_path=out_path,
            speaker_wav=speaker_path,
            language=lang_code,
        )
    else:
        print("👉 기본 화자(보이스 클로닝 없이) 사용")
        tts_model.tts_to_file(
            text=text,
            file_path=out_path,
            language=lang_code,
        )

    tts_embed = embed_audio(out_path)
    return tts_embed


# -----------------------------
# 채팅 히스토리 관리 함수
# -----------------------------
def clear_history():
    st.session_state.messages = []


def rewind():
    if st.session_state.messages:
        msg = st.session_state.messages.pop()
        while st.session_state.messages and msg.get("role", "") != "user":
            msg = st.session_state.messages.pop()


# -----------------------------
# Streamlit UI 시작
# -----------------------------
st.title("Peace Chatbot System (Gemini + XTTS v2)")

# 사이드바
with st.sidebar:
    st.header("Model")
    lang_display = st.selectbox("Language", language_names())
    lang_info = SUPPORTED_LANGUAGES[lang_display]
    lang_code = lang_info["code"]       # XTTS용 ("ko", "en", ...)
    lang_for_llm = lang_info["llm"]     # LLM 프롬프트용 ("Korean", "English", ...)

    TTS_MODEL = load_model()

    st.header("Control")
    gemini_api_key = st.text_input("GEMINI API Key", key="chatbot_api_key", type="password")
    voice_embed = st.toggle("Show Audio", value=True)
    btn_col1, btn_col2 = st.columns(2)
    with btn_col1:
        st.button("Rewind", on_click=rewind, use_container_width=True, type="primary")
    with btn_col2:
        st.button("Clear", on_click=clear_history, use_container_width=True)

    st.markdown("---")
    st.write("현재 사용 중인 화자 레퍼런스:")
    st.code(st.session_state.speaker_path or "기본 화자 (my_voice1.wav)", language="bash")

# -----------------------------
# 녹음 UI
# -----------------------------
st.subheader("Record your voice message")

audio = audiorecorder("녹음시작", "녹음정지")

# 새 녹음이 있으면 그걸 speaker_path로 교체
if len(audio) > 0:
    st.success("Recording complete!")
    with NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
        tmp_path = tmp_file.name
        audio.export(tmp_path, format="wav")
        st.write(f"저장된 파일: {tmp_path}")
        # 새 레퍼런스로 업데이트
        st.session_state.speaker_path = tmp_path

# -----------------------------
# 히스토리 표시
# -----------------------------
for i, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        content = msg.get("content", "")
        if voice_embed:
            embed = msg.get("tts_embed", "")
            # 마지막 메시지는 자동 재생
            if i == len(st.session_state.messages) - 1:
                embed = embed.replace("<audio controls>", "<audio controls autoplay>")
            if embed:
                content = "\n\n".join([content, embed])
        st.markdown(content, unsafe_allow_html=True)

# -----------------------------
# 채팅 입력 처리
# -----------------------------
if prompt := st.chat_input("Your message"):
    # user 메시지 표시
    with st.chat_message("user"):
        st.markdown(prompt, unsafe_allow_html=True)

    st.session_state.messages.append({"role": "user", "content": prompt})

    # assistant 응답
    with st.chat_message("assistant"):
        with st.spinner("Gemini & XTTS thinking..."):
            if not gemini_api_key:
                st.error("GEMINI API Key를 먼저 입력해주세요.")
            else:
                # Gemini LLM
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

                # 현재 speaker_path: 기본(my_voice1.wav) 또는 방금 녹음한 파일
                current_speaker = st.session_state.speaker_path

                tts_embed = tts_inference(
                    llm_response,
                    current_speaker,
                    TTS_MODEL,
                    lang_code,
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
