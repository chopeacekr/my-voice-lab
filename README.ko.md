# 🎙️ My Voice Lab

> **다른 언어로 읽기**: [English](./README.md) | [日本語](./README.ja.md)

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.29%2B-red)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Version](https://img.shields.io/badge/Version-0.3.0-orange)](CHANGELOG.md)

> **고급 오디오 분석 기능을 갖춘 멀티 TTS/STT 통합 시스템**

**5개의 TTS 모델**과 **4개의 STT 모델**을 통합한 Peace Chatbot 시스템. 오디오 시각화 및 분석 기능 포함.

![데모 스크린샷](./images/experimental_mode.png)

---

## ✨ 주요 기능

- 🎤 **멀티 STT 지원** - Google SR, Whisper, Wav2Vec2, Vosk
- 🔊 **멀티 TTS 지원** - gTTS, MeloTTS, XTTS v2, F5-TTS, Bark
- 🌍 **13개 언어** - 한국어, 영어, 일본어, 중국어, 프랑스어 등
- 🎨 **음성 복제** - XTTS v2 & F5-TTS 제로샷 음성 복제
- 🧪 **실험 모드** - Waveform/Spectrogram 시각화 + ZIP 내보내기
- 🤖 **Gemini LLM 통합** - Google Gemini와 자연스러운 대화
- ⚡ **서버 불필요** - gTTS + Google SR로 즉시 시작 (인터넷만 필요)
- 🏗️ **마이크로서비스 아키텍처** - 9개 독립 저장소

---

## 🚀 빠른 시작

### 사전 요구사항

- Python 3.11+
- 인터넷 연결 (gTTS & Google SR 사용)

### 설치

```bash
# 저장소 클론
git clone https://github.com/chopeacekr/my-voice-lab.git
cd my-voice-lab

# uv 설치 (없으면)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 의존성 설치
uv sync

# 실행!
uv run streamlit run web.py
```

브라우저 열기: **http://localhost:8501**

**끝!** 🎉 서버 설정 불필요.

---

## 📊 모델 비교

### TTS 모델

| 모델 | 속도 | 품질 | 서버 | 음성 복제 | 추천 용도 |
|------|------|------|------|-----------|----------|
| **gTTS** | ⚡⚡⚡ 0.5초 | ⭐⭐⭐ | 불필요 | ❌ | 빠른 시작 |
| **MeloTTS** | ⚡⚡ 1-2초 | ⭐⭐⭐⭐ | 필요 | ❌ | 실시간 |
| **XTTS v2** | ⚡ 5-10초 | ⭐⭐⭐⭐⭐ | 필요 | ✅ | 음성 복제 |
| **F5-TTS** | 10-20초 | ⭐⭐⭐⭐⭐ | 필요 | ✅ | 최고 품질 |
| **Bark** | 100-200초 | ⭐⭐⭐⭐⭐ | 필요 | ❌ | 감정/음악 |

### STT 모델

| 모델 | 속도 | 정확도 | 서버 | 오프라인 | 추천 용도 |
|------|------|--------|------|---------|----------|
| **Google SR** | ⚡⚡⚡ 0.8초 | 85% | 불필요 | ❌ | 빠른 시작 |
| **Whisper** | ⚡⚡ 1.3초 | 90% | 필요 | ✅ | 최고 정확도 |
| **Wav2Vec2** | ⚡⚡ 1.5초 | 82% | 필요 | ✅ | 한국어 최적화 |
| **Vosk** | ⚡⚡⚡ 0.9초 | 78% | 필요 | ✅ | 경량 |

---

## 🎮 사용법

### 기본 사용 (서버 불필요)

1. 앱 시작: `uv run streamlit run web.py`
2. 사이드바에서 **GEMINI API Key** 입력
3. **gTTS** (TTS)와 **Google SR** (STT) 선택
4. 🎤 클릭하여 녹음 → 말하기 → 중지
5. **Send** 클릭 → 음성으로 AI 응답 받기!

### 음성 복제 (XTTS v2)

1. TTS Model에서 **XTTS v2** 선택
2. "Record your voice sample"에서 🎤 클릭
3. 내 목소리 3-5초 녹음
4. 메시지 입력 후 **Send** 클릭
5. **내 목소리로** AI 응답! 🎉

### 실험 모드

1. **🧪 Experimental Mode** 토글 ON
2. 음성 녹음 → 자동 STT 인식
3. 오디오 플레이어와 함께 채팅 메시지 저장
4. **💾 저장 & 그래프 보기** 클릭
5. ZIP 파일 다운로드:
   - 원본 오디오 (WAV)
   - Waveform (PNG)
   - Spectrogram (PNG)

---

## 🏗️ 아키텍처

```
my-voice-lab/
├── web.py                    # 메인 Streamlit 앱
├── pyproject.toml           # 의존성
│
├── api_clients/
│   ├── tts/                 # TTS 클라이언트
│   │   ├── gtts_client.py
│   │   ├── melotts_client.py
│   │   ├── xtts_v2_client.py
│   │   ├── f5_client.py
│   │   └── bark_client.py
│   │
│   ├── stt/                 # STT 클라이언트
│   │   ├── gSR_client.py
│   │   ├── whisper_client.py
│   │   ├── wav2vec2_client.py
│   │   └── vosk_client.py
│   │
│   └── utils/               # 유틸리티
│       ├── audio_processor.py
│       └── audio_visualizer.py
│
└── [독립 저장소들]
    ├── my_melotts/          # MeloTTS 서버 (포트 8100)
    ├── my_xtts/             # XTTS v2 서버 (포트 8200)
    ├── my_f5/               # F5-TTS 서버 (포트 8500)
    ├── my_bark/             # Bark 서버 (포트 8600)
    ├── my_whisper/          # Whisper STT (포트 8300)
    ├── my_wav2vec2/         # Wav2Vec2 STT (포트 8400)
    └── my_vosk/             # Vosk STT (포트 8000)
```

**마이크로서비스 아키텍처**: 각 TTS/STT 모델은 독립적인 저장소와 서버로 실행됩니다.

---

## 🧪 실험 기능

### 오디오 시각화

**실험 모드**를 활성화하면:

- 🎧 **오디오 재생** - 녹음한 STT 입력 & TTS 출력 재생
- 📊 **Waveform** - 시간 영역 시각화
- 📈 **Spectrogram** - 주파수 영역 분석
- 💾 **ZIP 내보내기** - 오디오 + 그래프 다운로드

### 활용 사례

- 🔬 음성 품질 분석
- 📊 주파수 분석
- 💾 연구 데이터 수집
- 🎓 교육 자료

---

## 🛠️ 고급 설정

### 시스템 의존성

```bash
# Ubuntu/Debian
sudo apt-get install -y ffmpeg portaudio19-dev

# macOS
brew install ffmpeg portaudio
```

### 모든 모델 설치

각 TTS/STT 모델은 자체 서버가 필요합니다:

```bash
# 모든 저장소 클론
cd ~/myrepos
git clone https://github.com/chopeacekr/my_melotts.git
git clone https://github.com/chopeacekr/my_xtts.git
git clone https://github.com/chopeacekr/my_f5.git
git clone https://github.com/chopeacekr/my_bark.git
git clone https://github.com/chopeacekr/my_whisper.git
git clone https://github.com/chopeacekr/my_wav2vec2.git
git clone https://github.com/chopeacekr/my_vosk.git

# 각 서버 시작 (별도 터미널)
cd my_melotts && uv run python server_tts.py     # 포트 8100
cd my_xtts && uv run python server_tts.py        # 포트 8200
cd my_f5 && uv run python server_tts.py          # 포트 8500
cd my_bark && uv run python server_tts.py        # 포트 8600
cd my_whisper && uv run python server_stt.py     # 포트 8300
cd my_wav2vec2 && uv run python server_stt.py    # 포트 8400
cd my_vosk && uv run python server_stt.py        # 포트 8000
```

### 시스템 요구사항 (전체 설치)

- **RAM**: 16GB+
- **GPU**: NVIDIA 8GB+ (CUDA 11.8+)
- **디스크**: 20GB+

---

## 📚 문서

- **[REPORT.md](./REPORT.md)** - 상세 구현 보고서 (한국어)
- **[CHANGELOG.md](./CHANGELOG.md)** - 버전 히스토리
- **[CONTRIBUTING.md](./CONTRIBUTING.md)** - 기여 가이드

---

## 🐛 문제 해결

### ModuleNotFoundError: gtts_client

**문제**: 파일명 불일치 (`gTTS_client.py` vs `gtts_client.py`)

**해결**:
```bash
cd api_clients/tts
mv gTTS_client.py gtts_client.py
```

### gTTS 작동 안 함

**문제**: 인터넷 연결 없음 또는 Google TTS API 차단

**해결**:
- 인터넷 연결 확인
- 다른 TTS 사용 (MeloTTS)

### 서버 연결 실패

**문제**: 서버 미실행

**해결**:
```bash
cd ~/myrepos/my_xtts
uv run python server_tts.py
```

---

## 🤝 기여하기

기여를 환영합니다! 자세한 내용은 [CONTRIBUTING.md](./CONTRIBUTING.md)를 참고하세요.

### 개발 설정

```bash
# Fork 및 클론
git clone https://github.com/chopeacekr/my-voice-lab.git
cd my-voice-lab

# 브랜치 생성
git checkout -b feature/amazing-feature

# 개발 의존성 설치
uv sync --all-extras

# 변경 및 테스트
uv run streamlit run web.py

# 커밋 및 푸시
git commit -m "Add amazing feature"
git push origin feature/amazing-feature
```

---

## 📄 라이센스

이 프로젝트는 MIT 라이센스를 따릅니다 - [LICENSE](LICENSE) 파일 참고.

---

## 🙏 감사의 말

### 모델 & 라이브러리

- [gTTS](https://gtts.readthedocs.io/) - Google Text-to-Speech
- [MeloTTS](https://github.com/myshell-ai/MeloTTS) - 빠른 다국어 TTS
- [Coqui TTS](https://github.com/coqui-ai/TTS) - XTTS v2
- [F5-TTS](https://github.com/SWivid/F5-TTS) - 제로샷 음성 복제
- [Bark](https://github.com/suno-ai/bark) - 표현력 높은 TTS
- [Whisper](https://github.com/openai/whisper) - OpenAI STT
- [Wav2Vec2](https://huggingface.co/facebook/wav2vec2-base-960h) - Facebook STT
- [Vosk](https://alphacephei.com/vosk/) - 오프라인 STT

### 프레임워크

- [Streamlit](https://streamlit.io/) - 웹 프레임워크
- [LangChain](https://www.langchain.com/) - LLM 통합
- [Google Gemini](https://ai.google.dev/) - LLM
- [librosa](https://librosa.org/) - 오디오 분석
- [matplotlib](https://matplotlib.org/) - 시각화

---

## 📞 연락처

**Peace Cho**

- GitHub: [@chopeacekr](https://github.com/chopeacekr)
- Email: chopeacekr@gmail.com
- 프로젝트: [https://github.com/chopeacekr/my-voice-lab](https://github.com/chopeacekr/my-voice-lab)

---

## 🌟 Star History

[![Star History Chart](https://api.star-history.com/svg?repos=chopeacekr/my-voice-lab&type=Date)](https://star-history.com/#chopeacekr/my-voice-lab&Date)

---

<div align="center">

**Made with ❤️ by Peace Cho**

[⬆ 맨 위로](#-my-voice-lab)

</div>