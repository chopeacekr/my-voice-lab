# My Voice Lab - Multi-TTS Chatbot

Streamlit 기반 AI 음성 챗봇 시스템 - Gemini LLM과 MeloTTS/XTTS v2 TTS 엔진 통합

## 🎯 주요 기능

- **🤖 AI 대화**: Google Gemini 2.5 Flash 모델 기반 자연어 대화
- **🎤 음성 합성**: MeloTTS (빠름) 또는 XTTS v2 (화자 복제) 선택 가능
- **🌍 다국어 지원**: 한국어, 영어, 일본어, 프랑스어, 중국어 등 12개 언어
- **🎙️ 음성 녹음**: XTTS v2 화자 복제를 위한 실시간 녹음 기능
- **💬 채팅 히스토리**: 대화 내역 저장 및 되돌리기/초기화
- **🔊 오디오 자동재생**: 최신 응답 자동 재생

## 📋 시스템 요구사항

- **Python**: 3.11 이상
- **Package Manager**: UV
- **TTS 서버**: MeloTTS 또는 XTTS v2 (별도 실행 필요)
- **API Key**: Google Gemini API Key

## 🚀 설치 방법

### 1. 프로젝트 클론
```bash
git clone <repository-url>
cd my-voice-lab
```

### 2. UV를 사용한 의존성 설치
```bash
# 가상환경 생성 및 패키지 설치
uv sync
```

### 3. 주요 의존성
```toml
[project]
name = "my-voice-lab"
version = "0.1.0"
description = "TTS & STT"
requires-python = ">=3.11"

dependencies = [
    "streamlit",                    # 웹 UI 프레임워크
    "streamlit-audiorecorder",      # 음성 녹음 위젯
    "langchain-google-genai",       # Google Gemini LLM
    "requests>=2.32.5",             # HTTP 클라이언트 (TTS 서버 통신)
]
```

### 4. TTS 서버 설정 (필수)

최소 하나의 TTS 서버를 실행해야 합니다.

#### Option 1: MeloTTS 서버 (권장 - 빠름)
```bash
# 별도 터미널
cd ~/myrepos/MeloTTS
uv run uvicorn tts_server:app --host 0.0.0.0 --port 8000
```

#### Option 2: XTTS v2 서버 (화자 복제 필요 시)
```bash
# 별도 터미널
cd ~/myrepos/my_xtts_v2
uv run uvicorn server_tts:app --host 0.0.0.0 --port 8100
```

## 🎮 실행 방법

### Streamlit 앱 실행
```bash
cd my-voice-lab
uv run streamlit run web.py
```

브라우저에서 자동으로 `http://localhost:8501` 열림

### 사용 순서

1. **사이드바에서 설정**:
   - **TTS Model**: MeloTTS 또는 XTTS v2 선택
   - **Language**: 대화 언어 선택
   - **Gemini API Key**: 발급받은 API 키 입력
   - **LLM 요약 최대 글자 수**: 응답 길이 조절 (50~1000자)

2. **XTTS v2 사용 시 (선택)**:
   - "Record your voice sample" 섹션에서 음성 녹음
   - 녹음된 음성으로 목소리 복제

3. **채팅 시작**:
   - 하단 입력창에 메시지 입력
   - AI 응답 및 음성 자동 생성/재생

## 📁 프로젝트 구조
```
my-voice-lab/
├── web.py                      # Streamlit 메인 애플리케이션
├── api_clients/
│   ├── melotts_client.py      # MeloTTS HTTP 클라이언트
│   └── xtts_v2_client.py      # XTTS v2 HTTP 클라이언트
├── pyproject.toml             # 프로젝트 의존성
├── README.md                  # 이 문서
└── my_voice1.wav              # 기본 화자 샘플 (선택)
```

## 🔧 설정

### API 클라이언트 URL 변경

#### MeloTTS 서버 URL
`api_clients/melotts_client.py`:
```python
MELOTTS_SERVER_URL = "http://127.0.0.1:8000"
```

#### XTTS v2 서버 URL
`api_clients/xtts_v2_client.py`:
```python
XTTS_SERVER_URL = "http://127.0.0.1:8100"
```

### 지원 언어 목록
```python
SUPPORTED_LANGUAGES = {
    "Korean":     {"code": "ko", "melo": "KR"},
    "English":    {"code": "en", "melo": "EN"},
    "Japanese":   {"code": "en", "melo": "JP"},  # XTTS tokenizer 우회
    "French":     {"code": "fr", "melo": "FR"},
    "German":     {"code": "de", "melo": None},  # MeloTTS 미지원
    "Spanish":    {"code": "es", "melo": "ES"},
    "Italian":    {"code": "it", "melo": None},
    "Portuguese": {"code": "pt", "melo": None},
    "Polish":     {"code": "pl", "melo": None},
    "Turkish":    {"code": "tr", "melo": None},
    "Russian":    {"code": "ru", "melo": None},
    "Dutch":      {"code": "nl", "melo": None},
    "Chinese":    {"code": "zh", "melo": "ZH"},
}
```

### Gemini API Key 발급

1. [Google AI Studio](https://makersuite.google.com/app/apikey) 방문
2. API Key 생성
3. Streamlit 사이드바에 입력

또는 `.streamlit/secrets.toml` 파일에 저장:
```toml
GEMINI_API_KEY = "your-api-key-here"
```

## 🎚️ 주요 기능 설명

### TTS 모델 선택

#### MeloTTS (Fast & Multilingual)
- ⚡ **속도**: 매우 빠름 (1~2초)
- 💻 **하드웨어**: CPU 친화적
- 🎤 **화자**: 기본 화자만 사용
- 🌍 **언어**: KR, EN, JP, FR, ES, ZH

#### XTTS v2 (Voice Cloning)
- 🎭 **화자 복제**: 사용자 음성 복제 가능
- 🐢 **속도**: 느림 (8~10초)
- 🖥️ **하드웨어**: GPU 권장
- 🌍 **언어**: 14개 이상

### 채팅 컨트롤

- **Rewind**: 마지막 대화 쌍(유저+AI) 삭제
- **Clear**: 전체 대화 내역 초기화
- **Show Audio**: 오디오 플레이어 표시/숨김 토글

### 오디오 자동재생

- 최신 AI 응답만 자동 재생
- 이전 응답은 수동 클릭으로 재생
- 히스토리 스크롤 시 자동재생 비활성화

### 음성 녹음 (XTTS v2 전용)

1. "녹음시작" 버튼 클릭
2. 10~30초 동안 명확하게 발화
3. "녹음정지" 버튼 클릭
4. 자동으로 화자 레퍼런스로 저장

## 💻 사용 예시

### 기본 대화 흐름

1. **한국어로 대화**
```
   User: 오늘 날씨 어때?
   AI: 오늘은 맑고 화창한 날씨입니다. [🔊 음성 자동재생]
```

2. **언어 변경**
   - 사이드바에서 "English" 선택
```
   User: What's the weather today?
   AI: It's a clear and sunny day. [🔊 음성 자동재생]
```

3. **화자 복제 (XTTS v2)**
   - XTTS v2 모델 선택
   - 음성 녹음
   - 대화 시작 → 내 목소리로 합성됨

## 🐛 문제 해결

### 1. TTS 서버 연결 실패
```
RuntimeError: MeloTTS 서버 연결 실패
```

**확인사항**:
```bash
# MeloTTS 서버 상태 확인
curl http://localhost:8000/health

# XTTS v2 서버 상태 확인
curl http://localhost:8100/health
```

**해결책**: TTS 서버가 실행 중인지 확인

### 2. Gemini API Key 에러
```
Error: GEMINI API Key를 먼저 입력해주세요.
```

**해결책**: 
1. 사이드바에서 API Key 입력
2. 또는 `.streamlit/secrets.toml` 파일 생성:
```toml
   GEMINI_API_KEY = "your-key"
```

### 3. 타임아웃 에러
```
TTS 생성 중 오류가 발생했습니다: Read timed out
```

**원인**: XTTS v2 첫 요청은 느림 (정상)

**해결책**: 
- 첫 요청은 30~60초 소요 가능
- 재시도하면 빨라짐 (8~10초)

### 4. MeloTTS 언어 미지원 경고
```
⚠️ MeloTTS does not support German
```

**해결책**: 
- XTTS v2로 전환
- 또는 지원 언어 선택 (KR, EN, JP, FR, ES, ZH)

### 5. 일본어 문제

**증상**: 일본어 선택 시 XTTS v2 에러 발생

**원인**: XTTS v2 일본어 tokenizer 이슈

**해결책**: 
- 코드에서 자동으로 `lang="en"` 우회 처리됨
- MeloTTS는 `melo="JP"`로 정상 작동

## 📊 성능 비교

### TTS 모델 비교

| 항목 | MeloTTS | XTTS v2 |
|------|---------|---------|
| **속도** | 🚀 1~2초 | 🐢 8~10초 |
| **화자 복제** | ❌ 불가 | ✅ 가능 |
| **GPU 필요** | ❌ 불필요 | ✅ 권장 |
| **품질** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **지원 언어** | 6개 | 14개+ |
| **첫 요청** | ~2초 | ~30초 |
| **이후 요청** | ~1초 | ~8초 |

### 사용 권장

| 상황 | 권장 모델 |
|------|-----------|
| 빠른 응답 필요 | MeloTTS |
| 화자 복제 필요 | XTTS v2 |
| CPU만 사용 가능 | MeloTTS |
| GPU 사용 가능 | XTTS v2 |
| 대량 TTS 생성 | MeloTTS |
| 최고 음질 필요 | XTTS v2 |

## 🔐 환경 변수 설정

### Streamlit Secrets

`.streamlit/secrets.toml` 파일 생성:
```toml
# Gemini API Key
GEMINI_API_KEY = "your-gemini-api-key"

# TTS 서버 URL (선택)
MELOTTS_SERVER_URL = "http://127.0.0.1:8000"
XTTS_SERVER_URL = "http://127.0.0.1:8100"
```

### 환경 변수
```bash
# .env 파일
export GEMINI_API_KEY="your-api-key"
```

## 🎨 UI 커스터마이징

### Streamlit 설정

`.streamlit/config.toml`:
```toml
[theme]
primaryColor = "#FF4B4B"
backgroundColor = "#0E1117"
secondaryBackgroundColor = "#262730"
textColor = "#FAFAFA"

[server]
port = 8501
enableCORS = false
```

## 🔧 고급 설정

### 1. 포트 변경
```bash
uv run streamlit run web.py --server.port 8080
```

### 2. 외부 접속 허용
```bash
uv run streamlit run web.py --server.address 0.0.0.0
```

### 3. 자동 새로고침 비활성화
```bash
uv run streamlit run web.py --server.runOnSave false
```

### 4. LLM 모델 변경

`web.py` 파일에서:
```python
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",  # 모델 변경
    temperature=0,
    max_tokens=1024,
    google_api_key=gemini_api_key,
)
```

사용 가능한 모델:
- `gemini-2.5-flash`: 빠르고 효율적
- `gemini-1.5-pro`: 더 강력한 성능
- `gemini-1.5-flash`: 균형잡힌 성능

## 📱 모바일 지원

Streamlit은 반응형 디자인을 지원하여 모바일에서도 사용 가능합니다.

**접속 방법**:
1. 같은 네트워크에서 서버 실행
2. 모바일 브라우저에서 `http://<server-ip>:8501` 접속

## 🚀 배포

### Streamlit Cloud

1. GitHub에 코드 푸시
2. [Streamlit Cloud](https://streamlit.io/cloud) 연결
3. Secrets에 API Key 추가

⚠️ **주의**: TTS 서버는 별도 호스팅 필요

### Docker
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# UV 설치
RUN pip install uv

# 의존성 복사 및 설치
COPY pyproject.toml .
RUN uv sync

# 앱 복사
COPY . .

# 포트 노출
EXPOSE 8501

# 실행
CMD ["uv", "run", "streamlit", "run", "web.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

빌드 및 실행:
```bash
docker build -t my-voice-lab .
docker run -p 8501:8501 my-voice-lab
```

## 📝 라이선스

MIT License

## 🤝 기여

이슈 제보 및 풀 리퀘스트를 환영합니다!

### 기여 방법
1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📚 참고 자료

- [Streamlit Documentation](https://docs.streamlit.io/)
- [Google Gemini API](https://ai.google.dev/)
- [LangChain Documentation](https://python.langchain.com/)
- [MeloTTS GitHub](https://github.com/myshell-ai/MeloTTS)
- [Coqui XTTS v2](https://github.com/coqui-ai/TTS)

## 🙋 FAQ

**Q: Gemini API Key는 어디서 발급받나요?**  
A: [Google AI Studio](https://makersuite.google.com/app/apikey)에서 무료로 발급 가능합니다.

**Q: TTS 서버 없이 사용할 수 있나요?**  
A: 아니요, 최소 하나의 TTS 서버(MeloTTS 또는 XTTS v2)가 필요합니다.

**Q: 여러 언어를 동시에 사용할 수 있나요?**  
A: 언어는 대화별로 선택하며, 사이드바에서 언제든 변경 가능합니다.

**Q: 음성 녹음이 저장되나요?**  
A: 네, XTTS v2 화자 레퍼런스로 세션 동안 저장되며, 앱 종료 시 삭제됩니다.

**Q: 상업적으로 사용할 수 있나요?**  
A: MIT 라이선스로 상업적 사용 가능하지만, Gemini API 이용 약관을 확인하세요.

## 📧 문의

- **이슈 제보**: [GitHub Issues](링크)
- **이메일**: chopeacekr@gmail.com

## 🎉 감사의 글

- Google Gemini Team
- Coqui TTS Contributors
- MeloTTS Developers
- Streamlit Community

---

**Version**: 0.1.0  
**Last Updated**: 2024-11-26  
**Made with** ❤️ **by Peace Cho**