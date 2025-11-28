import base64
from tempfile import NamedTemporaryFile
import io

import streamlit as st
from audiorecorder import audiorecorder
from langchain_google_genai import ChatGoogleGenerativeAI
from pydub import AudioSegment

from api_clients.melotts_client import melotts_tts_http
from api_clients.xtts_v2_client import xtts_v2_tts_http
from api_clients.vosk_client import vosk_stt_http, check_vosk_health
from api_clients.whisper_client import whisper_stt_http, check_whisper_health


# ================================
# 언어 설정
# ================================
SUPPORTED_LANGUAGES = {
    "Korean":  {"code": "ko", "llm": "Korean", "melo": "KR", "vosk": "KR", "whisper": "KR"},
    "English": {"code": "en", "llm": "English", "melo": "EN", "vosk": "EN", "whisper": "EN"},
    "Japanese": {"code": "en", "llm": "Japanese", "melo": "JP", "vosk": "JP", "whisper": "JP"},
    "French": {"code": "fr", "llm": "French", "melo": "FR", "vosk": "FR", "whisper": "FR"},
    "German": {"code": "de", "llm": "German", "melo": None, "vosk": "DE", "whisper": "DE"},
    "Spanish": {"code": "es", "llm": "Spanish", "melo": "ES", "vosk": "ES", "whisper": "ES"},
    "Italian": {"code": "it", "llm": "Italian", "melo": None, "vosk": None, "whisper": None},
    "Portuguese": {"code": "pt", "llm": "Portuguese", "melo": None, "vosk": None, "whisper": None},
    "Polish": {"code": "pl", "llm": "Polish", "melo": None, "vosk": None, "whisper": None},
    "Turkish": {"code": "tr", "llm": "Turkish", "melo": None, "vosk": None, "whisper": None},
    "Russian": {"code": "ru", "llm": "Russian", "melo": None, "vosk": "RU", "whisper": "RU"},
    "Dutch": {"code": "nl", "llm": "Dutch", "melo": None, "vosk": None, "whisper": None},
    "Chinese": {"code": "zh", "llm": "Chinese", "melo": "ZH", "vosk": "ZH", "whisper": "ZH"},
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
    },
    "xtts_v2": {
        "label": "XTTS v2 (Voice Cloning)",
        "type": "xtts_v2",
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

# 👉 기본 TTS는 MeloTTS
if "tts_model_key" not in st.session_state:
    st.session_state.tts_model_key = "melotts"

# 👉 기본 STT는 Whisper (변경)
if "stt_model_key" not in st.session_state:
    st.session_state.stt_model_key = "whisper"

# 마지막 assistant 메시지 중 autoplay 대상 index
if "autoplay_index" not in st.session_state:
    st.session_state.autoplay_index = None

# Your message 입력값을 세션으로 관리 (STT 결과를 여기 넣어줄 것)
if "prompt_text" not in st.session_state:
    st.session_state.prompt_text = ""

# STT 처리 완료 플래그 (무한 루프 방지)
if "stt_processed" not in st.session_state:
    st.session_state.stt_processed = False

# audiorecorder 초기화를 위한 카운터
if "recorder_key_counter" not in st.session_state:
    st.session_state.recorder_key_counter = 0


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
# 오디오 전처리 함수 (NEW)
# ================================
def preprocess_audio_for_stt(audio_segment: AudioSegment, target_sample_rate: int = 16000) -> bytes:
    """
    STT를 위한 오디오 전처리
    - 스테레오 → 모노 변환
    - 샘플레이트 변환 (16kHz)
    - WAV 포맷으로 내보내기
    """
    # 스테레오 → 모노
    if audio_segment.channels > 1:
        audio_segment = audio_segment.set_channels(1)
    
    # 샘플레이트 변환
    if audio_segment.frame_rate != target_sample_rate:
        audio_segment = audio_segment.set_frame_rate(target_sample_rate)
    
    # WAV 바이트로 변환
    buffer = io.BytesIO()
    audio_segment.export(buffer, format="wav")
    return buffer.getvalue()


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

    cfg = TTS_MODEL_REGISTRY[model_key]
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
        return xtts_v2_tts_http(
            text=text,
            lang_code=lang_code,
            speaker_wav_path=speaker_path,
            speed=1.0,
        )

    print(f"⚠ Unsupported model type for inference: {model_type}")
    return ""


# ================================
# 공통 STT inference (수정)
# ================================
def stt_inference(
    model_key: str,
    audio_bytes: bytes,
    vosk_lang_code: str | None = None,
    whisper_lang_code: str | None = None,
) -> str:
    """
    model_key: "vosk" | "whisper"
    audio_bytes: WAV 오디오 데이터 (16kHz, 모노)
    vosk_lang_code: Vosk 언어 코드 ("KR", "EN", ...)
    whisper_lang_code: Whisper 언어 코드 ("KR", "EN", ...)
    """
    cfg = STT_MODEL_REGISTRY[model_key]
    model_type = cfg["type"]

    # ---------- Vosk (HTTP) ----------
    if model_type == "vosk":
        if not vosk_lang_code:
            raise ValueError("Vosk requires vosk_lang_code")
        print(f"👉 Vosk STT via HTTP: language={vosk_lang_code}")
        return vosk_stt_http(
            audio_bytes=audio_bytes,
            lang=vosk_lang_code,
            sample_rate=16000,
        )

    # ---------- Whisper (HTTP) ----------
    if model_type == "whisper":
        if not whisper_lang_code:
            whisper_lang_code = "KR"  # 기본값
        print(f"👉 Whisper STT via HTTP: language={whisper_lang_code}")
        return whisper_stt_http(
            audio_bytes=audio_bytes,
            lang=whisper_lang_code,
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
        # 마지막 assistant까지 같이 제거
        while st.session_state.messages and msg.get("role", "") != "user":
            msg = st.session_state.messages.pop()


# ================================
# Streamlit UI 시작
# ================================
st.title("Peace Chatbot System (Gemini + Multi-TTS/STT)")

with st.sidebar:
    # ========== TTS 모델 선택 ==========
    st.header("TTS Model")

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

    # ========== STT 모델 선택 ==========
    st.header("STT Model")

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

    # 서버 상태 확인
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

    # ========== 언어 선택 ==========
    st.header("Language")
    lang_display = st.selectbox("Language", language_names())
    lang_info = SUPPORTED_LANGUAGES[lang_display]
    lang_code = lang_info["code"]
    lang_for_llm = lang_info["llm"]
    melo_lang_code = lang_info.get("melo")
    vosk_lang_code = lang_info.get("vosk")
    whisper_lang_code = lang_info.get("whisper")

    # 언어 지원 경고
    if tts_model_key == "melotts" and not melo_lang_code:
        st.warning(
            f"⚠️ MeloTTS does not support {lang_display}. "
            "Please select another language or use XTTS v2."
        )

    if stt_model_key == "vosk" and not vosk_lang_code:
        st.warning(
            f"⚠️ Vosk does not support {lang_display} STT. "
            "Voice input will be disabled."
        )
    
    if stt_model_key == "whisper" and not whisper_lang_code:
        st.warning(
            f"⚠️ Whisper does not support {lang_display} STT. "
            "Voice input will be disabled."
        )

    # ========== 컨트롤 ==========
    st.header("Control")
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
        st.write("현재 사용 중인 화자 레퍼런스 (XTTS v2 용):")
        st.code(st.session_state.speaker_path or "기본 화자 (my_voice1.wav)", language="bash")
    else:
        st.info("MeloTTS는 화자 레퍼런스를 사용하지 않습니다.")


# ================================
# 녹음 UI (XTTS speaker reference 용)
# ================================
st.subheader("🎤 Record your voice sample (for XTTS speaker reference)")

audio = audiorecorder("녹음시작", "녹음정지", key="xtts_recorder")

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
# 채팅 입력 처리 (텍스트 + 음성)
# ================================
st.subheader("💬 Chat Input")

col1, col2 = st.columns([5, 1])

# ---- 오른쪽: 음성(STT) 녹음 버튼 (수정) ----
with col2:
    # Vosk 또는 Whisper 둘 중 하나라도 언어 지원하면 녹음 버튼 표시
    if (stt_model_key == "vosk" and vosk_lang_code) or \
       (stt_model_key == "whisper" and whisper_lang_code):
        # ✅ 동적 key로 audiorecorder 초기화 가능
        audio_stt = audiorecorder("🎤", "⏹️", key=f"stt_recorder_{st.session_state.recorder_key_counter}")
    else:
        audio_stt = None
        st.caption("STT 미지원")

# ========== 음성 입력 처리 (수정) ==========
prompt = None

# ✅ 오디오가 있고, 아직 처리하지 않았을 때만 STT 수행
if audio_stt and len(audio_stt) > 0 and not st.session_state.stt_processed:
    print("\n" + "="*80)
    print("🎤 [DEBUG] STT 처리 시작")
    print(f"   - audio_stt length: {len(audio_stt)}")
    print(f"   - stt_processed: {st.session_state.stt_processed}")
    print(f"   - recorder_key_counter: {st.session_state.recorder_key_counter}")
    print(f"   - current prompt_text: '{st.session_state.prompt_text}'")
    print("="*80)
    
    st.info("🎤 음성 입력 감지됨. 텍스트로 변환 중...")
    
    with st.spinner("Converting speech to text..."):
        try:
            # ✅ 오디오 전처리 (스테레오→모노, 리샘플링)
            print("📦 [DEBUG] 오디오 전처리 시작...")
            audio_bytes = preprocess_audio_for_stt(audio_stt, target_sample_rate=16000)
            print(f"✅ [DEBUG] 오디오 전처리 완료: {len(audio_bytes)} bytes")
            
            # 디버깅: 오디오 정보 출력
            st.caption(f"📊 Audio preprocessed: {len(audio_bytes)} bytes")
            
            # STT 처리
            print(f"🎯 [DEBUG] STT 처리 시작 (model: {st.session_state.stt_model_key})")
            transcribed_text = stt_inference(
                model_key=st.session_state.stt_model_key,
                audio_bytes=audio_bytes,
                vosk_lang_code=vosk_lang_code,
                whisper_lang_code=whisper_lang_code,
            )
            print(f"✅ [DEBUG] STT 처리 완료: '{transcribed_text}'")
            print(f"   - 텍스트 길이: {len(transcribed_text)}")
            print(f"   - strip 후 길이: {len(transcribed_text.strip())}")
            
            if transcribed_text.strip():
                print(f"✅ [DEBUG] 텍스트 인식 성공!")
                st.success(f"✅ 인식된 텍스트: {transcribed_text}")
                
                # STT 결과를 텍스트 입력창에 넣기
                print(f"📝 [DEBUG] prompt_text 업데이트 전: '{st.session_state.prompt_text}'")
                st.session_state.prompt_text = transcribed_text
                print(f"📝 [DEBUG] prompt_text 업데이트 후: '{st.session_state.prompt_text}'")
                
                # ✅ 처리 완료 플래그 설정
                st.session_state.stt_processed = True
                print(f"🚩 [DEBUG] stt_processed = True")
                
                # ✅ recorder 초기화 (key 변경으로 새 위젯 생성)
                old_counter = st.session_state.recorder_key_counter
                st.session_state.recorder_key_counter += 1
                print(f"🔄 [DEBUG] recorder_key_counter: {old_counter} → {st.session_state.recorder_key_counter}")
                
                print("🔄 [DEBUG] st.rerun() 호출...")
                st.rerun()
            else:
                print(f"⚠️  [DEBUG] 텍스트가 비어있음!")
                st.warning("⚠️ 음성이 인식되지 않았습니다. 다시 시도해주세요.")
                # 실패해도 플래그 설정하여 재시도 방지
                st.session_state.stt_processed = True
                # recorder 초기화
                st.session_state.recorder_key_counter += 1
                print("="*80 + "\n")
                
        except Exception as e:
            print(f"❌ [DEBUG] STT 처리 중 예외 발생: {e}")
            import traceback
            traceback.print_exc()
            print("="*80 + "\n")
            
            st.error(f"❌ STT 처리 실패: {e}")
            st.info(f"💡 {st.session_state.stt_model_key.capitalize()} 서버가 실행 중인지 확인하세요.")
            st.code(traceback.format_exc())
            # 에러 발생해도 플래그 설정
            st.session_state.stt_processed = True
            # recorder 초기화
            st.session_state.recorder_key_counter += 1
else:
    # 조건을 만족하지 않는 이유 디버깅
    if audio_stt and len(audio_stt) > 0:
        if st.session_state.stt_processed:
            print(f"⏭️  [DEBUG] STT 스킵: 이미 처리됨 (stt_processed=True)")
    elif audio_stt:
        print(f"⏭️  [DEBUG] STT 스킵: 오디오 없음 (len={len(audio_stt)})")

# ---- 왼쪽: 텍스트 입력창 (STT 결과가 여기로 들어감) ----
with col1:
    print(f"\n📝 [DEBUG] 텍스트 입력창 렌더링")
    print(f"   - session prompt_text: '{st.session_state.prompt_text}'")
    
    # ✅ key를 제거하고 value만 사용
    prompt_text = st.text_area(
        "Your message",
        value=st.session_state.prompt_text,  # 세션 값 사용
        height=80,
        # key 제거! 이것이 문제였음
    )
    
    print(f"   - 렌더된 text_area value: '{prompt_text}'")
    
    # 입력창 값 변경 시 세션 업데이트
    if prompt_text != st.session_state.prompt_text:
        print(f"🔄 [DEBUG] 사용자가 텍스트 수정함: '{st.session_state.prompt_text}' → '{prompt_text}'")
        st.session_state.prompt_text = prompt_text

# Send 버튼 (사용자가 직접 눌러야 LLM + TTS 실행)
send_clicked = st.button("Send", type="primary")

print(f"\n🔘 [DEBUG] Send 버튼 상태: {send_clicked}")
print(f"   - prompt_text: '{st.session_state.prompt_text}'")

# ========== 프롬프트가 있으면 처리 (오직 Send 눌렀을 때만) ==========
if send_clicked and st.session_state.prompt_text and st.session_state.prompt_text.strip():
    print(f"✅ [DEBUG] Send 조건 만족! LLM 처리 시작...")
    prompt = st.session_state.prompt_text.strip()

    with st.chat_message("user"):
        st.markdown(prompt, unsafe_allow_html=True)

    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        with st.spinner("Generating response..."):
            print("🤖 [DEBUG] assistant 메시지 블록 진입")
            if not gemini_api_key:
                print("❌ [DEBUG] API 키 없음")
                st.error("GEMINI API Key를 먼저 입력해주세요.")
                llm_response = ""
                tts_embed = ""
            else:
                print(f"✅ [DEBUG] API 키 확인됨 (길이: {len(gemini_api_key)}, 시작: {gemini_api_key[:10]}...)")
                
                # API 키 형식 검증
                if not gemini_api_key.startswith("AIza"):
                    print(f"⚠️  [DEBUG] API 키 형식이 이상함 - Gemini API 키는 'AIza'로 시작해야 함")
                    st.error("⚠️ Gemini API 키 형식이 올바르지 않습니다. 'AIza'로 시작하는 키를 입력해주세요.")
                    llm_response = ""
                    tts_embed = ""
                    return
                # TTS 언어 지원 체크
                if tts_model_key == "melotts" and not melo_lang_code:
                    print(f"❌ [DEBUG] MeloTTS 언어 미지원: {lang_display}")
                    st.error(
                        f"MeloTTS does not support {lang_display}. "
                        "Please select another language or model."
                    )
                    llm_response = ""
                    tts_embed = ""
                else:
                    print(f"📞 [DEBUG] LLM 호출 준비 (model: gemini-2.5-flash)")
                    try:
                        llm = ChatGoogleGenerativeAI(
                            model="gemini-2.5-flash",  # ✅ 최신 2.5 flash 모델
                            temperature=0,
                            max_tokens=1024,
                            google_api_key=gemini_api_key,
                        )
                        print(f"✅ [DEBUG] LLM 객체 생성 완료")
                    except Exception as e:
                        print(f"❌ [DEBUG] LLM 객체 생성 실패: {e}")
                        raise

                    print(f"📤 [DEBUG] LLM invoke 시작...")
                    try:
                        raw_resp = llm.invoke(
                            prompt
                            + f"\nPlease answer in {lang_for_llm}, and keep it short, under {llm_max_chars} characters."
                        ).content
                        print(f"✅ [DEBUG] LLM 응답 받음: {len(raw_resp) if raw_resp else 0} chars")
                    except Exception as e:
                        print(f"❌ [DEBUG] LLM 호출 실패: {e}")
                        error_msg = str(e)
                        if "429" in error_msg or "quota" in error_msg.lower():
                            st.error("⚠️ Gemini API 할당량 초과")
                            st.info("💡 잠시 후 다시 시도하거나, API 키를 확인해주세요.")
                            st.caption("Free tier는 분당 요청 제한이 있습니다. 약 1분 후 다시 시도해주세요.")
                            raw_resp = None
                        else:
                            st.error(f"❌ LLM 요청 실패: {e}")
                            raw_resp = None

                    llm_response = (raw_resp or "").strip()
                    print(f"📝 [DEBUG] LLM 응답 정리됨: '{llm_response[:50]}...' ({len(llm_response)} chars)")

                    if not llm_response:
                        print("⚠️  [DEBUG] LLM 응답 비어있음")
                        st.warning("LLM 응답이 비어 있어 TTS를 건너뜁니다.")
                        tts_embed = ""
                    else:
                        st.markdown(llm_response)
                        print(f"🔊 [DEBUG] TTS 생성 시작 (model: {st.session_state.tts_model_key})")
                        current_speaker = st.session_state.speaker_path

                        try:
                            tts_embed = tts_inference(
                                model_key=st.session_state.tts_model_key,
                                text=llm_response,
                                speaker_path=current_speaker,
                                lang_code=lang_code,
                                melo_lang_code=melo_lang_code,
                            )
                            print(f"✅ [DEBUG] TTS 생성 완료")
                        except Exception as e:
                            print(f"❌ [DEBUG] TTS 생성 실패: {e}")
                            st.error(f"⚠️ TTS 생성 실패: {e}")
                            st.info("💡 첫 요청은 모델 로딩으로 시간이 오래 걸릴 수 있습니다. 다시 시도해보세요.")
                            tts_embed = ""

                        if tts_embed:
                            st.markdown(tts_embed, unsafe_allow_html=True)
                            print(f"✅ [DEBUG] TTS 오디오 표시됨")

            # assistant 메시지 push
            print(f"💾 [DEBUG] assistant 메시지 저장")
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": llm_response,
                    "tts_embed": tts_embed if voice_embed else "",
                }
            )

            # 👉 방금 추가한 assistant 메시지만 autoplay 대상으로 지정
            st.session_state.autoplay_index = len(st.session_state.messages) - 1
            print(f"✅ [DEBUG] assistant 메시지 블록 완료")

    # 한 번 보낸 프롬프트는 입력창에서 비워줌
    print(f"\n🧹 [DEBUG] Send 완료 후 정리")
    print(f"   - prompt_text 초기화 전: '{st.session_state.prompt_text}'")
    st.session_state.prompt_text = ""
    print(f"   - prompt_text 초기화 후: '{st.session_state.prompt_text}'")
    
    # ✅ STT 플래그 초기화 (새 녹음 가능하도록)
    print(f"   - stt_processed 초기화 전: {st.session_state.stt_processed}")
    st.session_state.stt_processed = False
    print(f"   - stt_processed 초기화 후: {st.session_state.stt_processed}")
    print("🔄 [DEBUG] st.rerun() 호출...\n")
    st.rerun()