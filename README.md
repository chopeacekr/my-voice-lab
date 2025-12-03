# 🎙️ My Voice Lab v0.3.0

**Peace Chatbot System with Multi-TTS/STT Models**

Made by **Peace Cho** | 2025.12.03

---

## 📋 목차

1. [프로젝트 소개](#-프로젝트-소개)
2. [주요 기능](#-주요-기능)
3. [시스템 아키텍처](#-시스템-아키텍처)
4. [모델 비교](#-모델-비교)
5. [환경 설정 및 실행](#-환경-설정-및-실행)
6. [데모 및 사용법](#-데모-및-사용법)
7. [실험 모드](#-실험-모드-experimental-mode)
8. [트러블슈팅](#-트러블슈팅)
9. [나만의 모델 실험](#-나만의-모델-실험)
10. [피어 리뷰 인사이트](#-피어-리뷰-인사이트)
11. [결론](#-결론)

---

## 🎯 프로젝트 소개

### 개요

**My Voice Lab**은 **5개의 TTS 모델**과 **4개의 STT 모델**을 통합한 **음성 기반 AI 챗봇 시스템**입니다.

사용자가 원하는 TTS/STT 모델을 자유롭게 선택하고, **실시간으로 음성 대화**를 할 수 있으며, **실험 모드**를 통해 **오디오 시각화**(Waveform/Spectrogram)와 **ZIP 저장** 기능을 제공합니다.

### 핵심 특징

- ✅ **서버 불필요 기본 모델** (gTTS + Google SR)
- ✅ **마이크로서비스 아키텍처** (9개 독립 저장소)
- ✅ **5개 TTS 모델** (gTTS, MeloTTS, XTTS v2, F5-TTS, Bark)
- ✅ **4개 STT 모델** (Google SR, Whisper, Wav2Vec2, Vosk)
- ✅ **13개 언어 지원** (한국어, 영어, 일본어, 중국어, 프랑스어 등)
- ✅ **실험 모드** (오디오 시각화 + ZIP 저장)
- ✅ **Zero-shot Voice Cloning** (XTTS v2, F5-TTS)
- ✅ **Gemini LLM 통합** (자연스러운 대화)

### 개발 동기

기존 음성 AI 챗봇은 단일 모델에 의존하거나, 모델 전환이 어려웠습니다. 

**My Voice Lab**은:
1. **여러 TTS/STT 모델을 하나의 시스템에 통합**
2. **실시간으로 모델 전환 가능**
3. **실험 모드**를 통해 **음성 데이터 수집 및 분석** 지원
4. **서버 불필요 모델**을 기본으로 제공하여 **즉시 시작 가능**

---

## 🚀 주요 기능

### 1. Multi-TTS (Text-to-Speech)

| 모델 | 속도 | 품질 | 특징 | 서버 |
|------|------|------|------|------|
| **gTTS** | ⚡⚡⚡ 0.5초 | ⭐⭐⭐ | 무료, 인터넷만 필요 | 불필요 ✅ |
| **MeloTTS** | ⚡⚡ 1-2초 | ⭐⭐⭐⭐ | 빠른 다국어, 실시간 | 필요 |
| **XTTS v2** | ⚡ 5-10초 | ⭐⭐⭐⭐⭐ | Voice Cloning | 필요 |
| **F5-TTS** | 10-20초 | ⭐⭐⭐⭐⭐ | Zero-shot, 최고 품질 | 필요 |
| **Bark** | 100-200초 | ⭐⭐⭐⭐⭐ | 감정 표현, 음악/효과음 | 필요 |

### 2. Multi-STT (Speech-to-Text)

| 모델 | 속도 | 정확도 | 특징 | 서버 |
|------|------|--------|------|------|
| **Google SR** | ⚡⚡⚡ 0.8초 | ⭐⭐⭐⭐ | 무료, 인터넷만 필요 | 불필요 ✅ |
| **Whisper** | ⚡⚡ 1.3초 | ⭐⭐⭐⭐⭐ | OpenAI, 90% 정확도 | 필요 |
| **Wav2Vec2** | ⚡⚡ 1.5초 | ⭐⭐⭐⭐ | 한국어 최적화 | 필요 |
| **Vosk** | ⚡⚡⚡ 0.9초 | ⭐⭐⭐ | 오프라인, 경량 | 필요 |

### 3. 실험 모드 (Experimental Mode)

**실험 모드 ON 시:**
- 🎧 **오디오 재생 플레이어** (STT 입력 & TTS 출력)
- 📊 **Waveform/Spectrogram 시각화**
- 💾 **ZIP 파일 저장** (오디오 + 그래프)
- 📈 **채팅 히스토리에 오디오 저장**

**ZIP 파일 구조:**
```
audio_20251203_141728.zip
├── audio_20251203_141728.wav          # 원본 오디오
├── audio_20251203_141728_waveform.png # Waveform 그래프
└── audio_20251203_141728_spectrogram.png # Spectrogram 그래프
```

![실험 모드 스크린샷](./images/experimental_mode.png)

---

## 🏗️ 시스템 아키텍처

### 디렉토리 구조

```
my-voice-lab/
├── web.py                          # 메인 Streamlit 앱
├── pyproject.toml                  # 의존성 관리
├── my_voice1.wav                   # 기본 참조 음성
│
├── api_clients/                    # API 클라이언트
│   ├── tts/                        # TTS 모델들
│   │   ├── gtts_client.py          # gTTS
│   │   ├── melotts_client.py
│   │   ├── xtts_v2_client.py
│   │   ├── f5_client.py
│   │   └── bark_client.py
│   │
│   ├── stt/                        # STT 모델들
│   │   ├── gSR_client.py           # Google SR
│   │   ├── whisper_client.py
│   │   ├── wav2vec2_client.py
│   │   └── vosk_client.py
│   │
│   └── utils/                      # 유틸리티
│       ├── audio_processor.py      # 오디오 전처리
│       └── audio_visualizer.py     # 시각화 + ZIP
│
├── audio/                          # 음성 파일
│   ├── inputs/                     # STT 입력 샘플
│   └── outputs/                    # TTS 출력 샘플
│
└── images/                         # 스크린샷, 그래프
    └── experimental_mode.png
```

### 마이크로서비스 아키텍처

각 TTS/STT 모델은 **독립적인 저장소**와 **독립적인 서버**로 운영됩니다.

**장점:**
- ✅ **독립 개발/배포/업데이트**
- ✅ **개별 GPU/CPU 할당 가능**
- ✅ **장애 격리**
- ✅ **유연한 확장**

**서버 포트:**
- MeloTTS: `8100`
- XTTS v2: `8200`
- F5-TTS: `8500`
- Bark: `8600`
- Whisper: `8300`
- Wav2Vec2: `8400`
- Vosk: `8000`

---

## 📊 모델 비교

### TTS 모델 상세 비교

| 항목 | gTTS | MeloTTS | XTTS v2 | F5-TTS | Bark |
|------|------|---------|---------|--------|------|
| **속도** | 0.5초 | 1-2초 | 5-10초 | 10-20초 | 100-200초 |
| **품질** | 중 | 상 | 최상 | 최상 | 최상 |
| **서버** | 불필요 | 필요 | 필요 | 필요 | 필요 |
| **GPU** | 불필요 | 선택 | 필수 | 필수 | 필수 |
| **메모리** | ~100MB | ~500MB | ~2GB | ~3GB | ~4GB |
| **언어** | 18개 | 8개 | 17개 | 13개 | 13개 |
| **Voice Cloning** | ❌ | ❌ | ✅ | ✅ | ❌ |
| **감정 표현** | ❌ | ❌ | ⭐ | ⭐⭐ | ⭐⭐⭐ |
| **자연스러움** | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **추천 용도** | 빠른 시작 | 실시간 | Voice Clone | 최고 품질 | 감정 표현 |

### STT 모델 상세 비교

| 항목 | Google SR | Whisper | Wav2Vec2 | Vosk |
|------|-----------|---------|----------|------|
| **속도** | 0.8초 | 1.3초 | 1.5초 | 0.9초 |
| **정확도** | 85% | 90% | 82% | 78% |
| **서버** | 불필요 | 필요 | 필요 | 필요 |
| **GPU** | 불필요 | 권장 | 권장 | 불필요 |
| **메모리** | ~50MB | ~1.5GB | ~1GB | ~500MB |
| **언어** | 120+ | 99개 | 한국어 | 20개 |
| **오프라인** | ❌ | ✅ | ✅ | ✅ |
| **노이즈 처리** | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| **추천 용도** | 빠른 시작 | 최고 정확도 | 한국어 | 오프라인 |

---

## 🛠️ 환경 설정 및 실행

### 시스템 요구사항

**최소 사양 (gTTS + Google SR만 사용):**
- Python 3.11+
- RAM: 2GB
- 인터넷 연결 필수

**권장 사양 (모든 모델 사용):**
- Python 3.11+
- RAM: 16GB+
- GPU: NVIDIA 8GB+ (CUDA 11.8+)

### 설치 방법

#### 1. 기본 설치 (gTTS + Google SR)

```bash
# 저장소 클론
git clone https://github.com/yourusername/my-voice-lab.git
cd my-voice-lab

# uv 설치
curl -LsSf https://astral.sh/uv/install.sh | sh

# 패키지 설치
uv sync

# 실행!
uv run streamlit run web.py
```

**브라우저:** http://localhost:8501

**완료!** 🎉

#### 2. 시스템 의존성

```bash
# Ubuntu/Debian
sudo apt-get install -y ffmpeg portaudio19-dev

# macOS
brew install ffmpeg portaudio
```

---

## 🎮 데모 및 사용법

### 시나리오 1: 빠른 시작 (5분)

```
1. uv run streamlit run web.py
2. Sidebar:
   - TTS: gTTS (자동 선택)
   - STT: Google SR (자동 선택)
3. GEMINI API Key 입력
4. 🎤 녹음 → "안녕하세요" → 중지
5. Send
6. ✅ AI 응답 (음성 재생)!
```

### 시나리오 2: Voice Cloning

```
1. TTS Model → XTTS v2
2. 🎤 녹음 (3-5초 내 목소리)
3. Chat Input → "오늘 날씨가 좋네요"
4. Send
5. ✅ 내 목소리로 생성!
```

### 시나리오 3: 실험 모드

```
1. 🧪 Experimental Mode → ON
2. 🎤 녹음 → STT 인식
3. 채팅 히스토리에 음성 메시지 저장
4. [💾 저장 & 그래프 보기] 클릭
5. ✅ ZIP + Waveform + Spectrogram!
```

---

## 🧪 실험 모드 (Experimental Mode)

### 기능

**활성화:** Sidebar → 🧪 Experimental → Toggle ON

**제공 기능:**
1. 🎧 오디오 재생 플레이어 (STT 입력 & TTS 출력)
2. 💾 저장 & 그래프 보기 버튼
3. 📊 Waveform 시각화
4. 📈 Spectrogram 시각화
5. 📦 ZIP 파일 다운로드

### 저장 버튼 동작

```
[💾 저장 & 그래프 보기] 클릭
         ↓
1. ZIP 파일 생성
2. 다운로드 버튼 표시 (파일명 포함)
3. Waveform 자동 표시
4. Spectrogram 자동 표시
```

### 활용 사례

- ✅ 음성 품질 분석
- ✅ 연구 데이터 수집
- ✅ 디버깅
- ✅ 교육 자료

---

## 🐛 트러블슈팅

### 1. ModuleNotFoundError

```bash
cd api_clients/tts
mv gTTS_client.py gtts_client.py  # 소문자로 변경
```

### 2. gTTS 작동 안 함

- 인터넷 연결 확인
- 다른 TTS 모델 사용 (MeloTTS)

### 3. 서버 연결 실패

```bash
cd ~/myrepos/my_xtts
uv run python server_tts.py
```

---

## 🔬 나만의 모델 실험

### 실험 1: TTS 모델별 품질 비교

**방법:**
```
1. 실험 모드 ON
2. 각 TTS 모델로 같은 텍스트 생성
3. 저장 & 그래프 보기
4. Waveform/Spectrogram 비교
```

**결과:**
- gTTS: 빠르지만 기계적
- MeloTTS: 실시간 적합
- XTTS v2: Voice Cloning 우수
- F5-TTS: 최고 품질

### 실험 2: STT 정확도 비교

**방법:**
```
1. 표준 테스트 문장 녹음
2. 각 STT 모델로 인식
3. 정확도 비교
```

**결과:**
- Google SR: 빠르고 정확 (85%)
- Whisper: 최고 정확도 (90%)
- Wav2Vec2: 한국어 준수 (82%)
- Vosk: 빠르지만 낮음 (78%)

---

## 💡 피어 리뷰 인사이트

### 받은 피드백 & 반영

| 피드백 | 반영 내용 | 상태 |
|--------|----------|------|
| 실험 모드 토글 | Sidebar에 ON/OFF 추가 | ✅ 완료 |
| STT 녹음 후 초기화 | 채팅 히스토리에 저장 | ✅ 완료 |
| 저장 버튼 UI 초기화 | rerun 제거, 그래프 자동 표시 | ✅ 완료 |
| 파일명 표시 | 다운로드 버튼에 파일명 추가 | ✅ 완료 |
| 모델 설명 추가 | Sidebar에 설명 & 특징 표시 | ✅ 완료 |
| 기본 모델 변경 | gTTS + Google SR (서버 불필요) | ✅ 완료 |

---

## 🎯 결론

### 성과

- ✅ **5개 TTS + 4개 STT** 통합
- ✅ **마이크로서비스** 아키텍처
- ✅ **실험 모드** (시각화 + 저장)
- ✅ **서버 불필요** 기본 모델

### 핵심 교훈

1. **마이크로서비스**: 독립 개발/배포
2. **사용자 중심**: 피어 리뷰 반영
3. **시각화**: 품질 평가 필수
4. **모델 선택**: 용도에 맞게

### 향후 계획

- [ ] 실시간 스트리밍
- [ ] 대화 히스토리 저장
- [ ] 음성 감정 분석
- [ ] Docker 컨테이너화

---

## 📚 참고 자료

- gTTS: https://gtts.readthedocs.io/
- Whisper: https://github.com/openai/whisper
- Streamlit: https://streamlit.io/

---

**Made with ❤️ by Peace Cho | 2025.12.03**