import base64
from tempfile import NamedTemporaryFile

import streamlit as st
from audiorecorder import audiorecorder
from langchain_google_genai import ChatGoogleGenerativeAI

from api_clients.melotts_client import melotts_tts_http
from api_clients.xtts_v2_client import xtts_v2_tts_http


# ================================
# 언어 설정
# ================================
SUPPORTED_LANGUAGES = {
    "Korean":  {"code": "ko", "llm": "Korean", "melo": "KR"},
    "English": {"code": "en", "llm": "English", "melo": "EN"},
    # XTTS에서 일본어는 tokenizer 문제 때문에 일단 lang="en"으로 우회,
    # MeloTTS는 melo="JP"로 정상 일본어 사용
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
    "melotts": {
        "label": "MeloTTS (Fast & Multilingual, via HTTP)",
        "type": "melotts",
    },
    "xtts_v2": {
        "label": "XTTS v2 (Coqui, Voice Cloning via HTTP)",
        "type": "xtts_v2",
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
DEFAULT_SPEAKER_WAV = "my_voice1.wav"

if "messages" not in st.session_state:
    st.session_state.messages = []

if "speaker_path" not in st.session_state:
    st.session_state.speaker_path = DEFAULT_SPEAKER_WAV

# 👉 기본 TTS는 MeloTTS
if "tts_model_key" not in st.session_state:
    st.session_state.tts_model_key = "melotts"

# 마지막 assistant 메시지 중 autoplay 대상 index
if "autoplay_index" not in st.session_state:
    st.session_state.autoplay_index = None


# ================================
# (예비) 로컬 파일용 embed 유틸
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
    text: str | None,
    speaker_path: str | None,
    lang_code: str,
    melo_lang_code: str | None = None,
) -> str:
    """
    model_key: "melotts" | "xtts_v2"
    text: 생성할 텍스트 (None 또는 공백이면 바로 스킵)
    speaker_path: XTTS에서 사용할 speaker reference wav 경로 (선택)
    lang_code: XTTS 언어 코드 ("ko", "en", ...)
    melo_lang_code: MeloTTS 언어 코드 ("KR", "EN", ...), 없으면 사용 불가
    """
    if text is None:
        return ""
    text = text.strip()
    if not text:
        return ""

    cfg = MODEL_REGISTRY[model_key]
    model_type = cfg["type"]

    # ---------- MeloTTS (HTTP) ----------
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

    # ---------- XTTS v2 (HTTP) ----------
    if model_type == "xtts_v2":
        print(f"👉 XTTS v2 via HTTP: language={lang_code}")
        # speaker_path는 사용자가 녹음한 wav (없으면 기본 화자 사용)
        return xtts_v2_tts_http(
            text=text,
            lang_code=lang_code,
            speaker_wav_path=speaker_path,
            speed=1.0,
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
        # 마지막 assistant까지 같이 제거
        while st.session_state.messages and msg.get("role", "") != "user":
            msg = st.session_state.messages.pop()


# ================================
# Streamlit UI 시작
# ================================
st.title("Peace Chatbot System (Gemini + MeloTTS / XTTS v2)")

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

    # MeloTTS 선택 시 지원하지 않는 언어 경고
    if model_key == "melotts" and not melo_lang_code:
        st.warning(
            f"⚠️ MeloTTS does not support {lang_display}. "
            "Please select another language or use XTTS v2."
        )

    st.header("Control")
    gemini_api_key = st.text_input(
        "GEMINI API Key",
        key="chatbot_api_key",
        type="password",
    )

    # 🔹 LLM 요약 최대 글자 수 설정
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
    if model_key == "xtts_v2":
        st.write("현재 사용 중인 화자 레퍼런스 (XTTS v2 용):")
        st.code(st.session_state.speaker_path or "기본 화자 (my_voice1.wav)", language="bash")
    else:
        st.info("MeloTTS(HTTP)는 화자 레퍼런스를 사용하지 않습니다. (녹음은 XTTS용 기준)")


# ================================
# 녹음 UI (항상 표시: XTTS speaker reference 용)
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
# 히스토리 표시 (autoplay는 마지막 assistant 메시지 중 '딱 한 번만')
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

# 렌더 후에는 autoplay 플래그 초기화
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
                llm_response = ""
                tts_embed = ""
            else:
                # MeloTTS 선택 시 지원하지 않는 언어 체크
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

                        try:
                            tts_embed = tts_inference(
                                model_key=st.session_state.tts_model_key,
                                text=llm_response,
                                speaker_path=current_speaker,
                                lang_code=lang_code,
                                melo_lang_code=melo_lang_code,
                            )
                        except Exception as e:
                            st.error(f"⚠️ TTS 생성 실패: {e}")
                            st.info("💡 첫 요청은 모델 로딩으로 시간이 오래 걸릴 수 있습니다. 다시 시도해보세요.")
                            tts_embed = ""

                        if tts_embed:
                            st.markdown(tts_embed, unsafe_allow_html=True)

            # assistant 메시지 push
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": llm_response,
                    "tts_embed": tts_embed if voice_embed else "",
                }
            )

            # 👉 방금 추가한 assistant 메시지만 autoplay 대상으로 지정
            st.session_state.autoplay_index = len(st.session_state.messages) - 1

    st.rerun()
