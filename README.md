# 🗣️ TTS 모델 성능평가용 챗봇 시스템

이 저장소는 **XTTS v2 / MeloTTS / 사용자 커스텀 TTS 모델**의 음성 품질을 빠르게 비교하고 평가하기 위해 설계된 **Streamlit 기반 챗봇 시스템**입니다.

텍스트 입력 → TTS 모델 선택 → 음성 생성 → 대화형 평가  
까지 한 번에 가능하며 LangChain 을 이용한 자동 평가도 지원합니다.

my-voice-lab 구성

# 1) MeloTTS 서버
cd ~/myrepos/MeloTTS
uv run uvicorn tts_server:app --host 0.0.0.0 --port 8000

# 2) XTTS v2 서버
cd ~/myrepos/my_xtts_v2
uv run uvicorn server_tts:app --host 0.0.0.0 --port 8100

# 3) Web UI
cd ~/myrepos/my_voice_lab
uv run streamlit run web.py

---

## 🔗 관련 문서

- 👉 **XTTS v2 상세 설명 (XTTS_V2_README.md)**  
  (같은 저장소 내부 파일)
  
- 👉 **my MeloTTS API 서비스(GitHub)**  
  https://github.com/chopeacekr/my_melotts
  

---

# ⚙️ 설치 방법 (Ubuntu 24.04.01 + Python 3.12)

## 1. 프로젝트 초기화

```bash
uv init xttsv2
cd xttsv2
```

## 2. PyTorch CPU 버전 설치

```bash
uv pip install "torch==2.3.1" "torchaudio==2.3.1" --index-url https://download.pytorch.org/whl/cpu
```

## 3. 핵심 라이브러리 설치

```bash
uv pip install "coqui-tts==0.25.3" "transformers==4.46.2"
```

## 4. 시스템 패키지 설치

```bash
sudo apt update
sudo apt install ffmpeg -y
sudo apt install -y portaudio19-dev
```

## 5. 한국어 텍스트 처리 (hangul_romanize)

```bash
uv pip install hangul-romanize
```

## 6. Streamlit + LangChain + Audio Recorder

```bash
uv pip install streamlit
uv pip install langchain
uv pip install langchain-google-genai
uv pip install streamlit-audiorecorder
```

## 7. 패키지 리스트 저장

```bash
pip freeze > requirements.txt
```

## 8. 실행

```bash
uv run streamlit run web.py
```

---

# 🧪 챗봇 시스템 기능 개요

### ✔ 1) TTS 모델 선택 및 비교

- XTTS v2
- MeloTTS
- Custom TTS 모델

### ✔ 2) LangChain 기반 자동 평가

- 발음 정확도
- 자연스러움
- 감정 표현
- 음질 평가

### ✔ 3) 음성 녹음 기반 화자 클로닝 평가

---

---
# MeloTTS vs XTTS v2 비교

## 주요 차이점

### 모델 로딩
- **MeloTTS**: 언어별 lazy load (첫 요청 시 로딩)
- **XTTS v2**: 서버 시작 시 한 번만 로딩

### 화자 복제 (Voice Cloning)
- **MeloTTS**: ❌ 불가능 (기본 화자만 사용)
- **XTTS v2**: ✅ 가능 (사용자 음성 샘플로 복제)

### 처리 속도
- **MeloTTS**: 🚀 매우 빠름 (1~2초)
- **XTTS v2**: 🐢 느림 (8~10초)

### 메모리 캐싱
- **MeloTTS**: 언어별 모델 개별 캐싱
- **XTTS v2**: 단일 모델 (모든 언어 공유)

### 하드웨어
- **MeloTTS**: CPU 권장 (가볍고 빠름)
- **XTTS v2**: GPU 권장 (CUDA 필요)

### 지원 언어
- **MeloTTS**: KR, EN, JP, FR, ES, ZH (6개 언어)
- **XTTS v2**: 다국어 지원 (14개 이상)

### 첫 요청 시간
- **MeloTTS**: ~3초 (모델 로딩 + 합성)
- **XTTS v2**: ~10초 (화자 임베딩 + 합성)

### 두 번째 요청부터
- **MeloTTS**: ~1초 (모델 캐싱됨)
- **XTTS v2**: ~8초 (화자 임베딩은 매번 새로 생성)

## 사용 시나리오

### MeloTTS 추천
- 빠른 응답이 필요한 경우
- 화자 복제가 필요 없는 경우
- CPU만 사용 가능한 환경
- 대량의 TTS 처리 (비용 절감)

### XTTS v2 추천
- 특정 사람 목소리 복제가 필요한 경우
- GPU 사용 가능한 환경
- 음질과 자연스러움이 최우선인 경우
- 처리 시간보다 품질이 중요한 경우

## 품질 비교

### 음질
- **MeloTTS**: ⭐⭐⭐⭐ 우수
- **XTTS v2**: ⭐⭐⭐⭐⭐ 매우 우수

### 자연스러움
- **MeloTTS**: ⭐⭐⭐⭐ 자연스러움
- **XTTS v2**: ⭐⭐⭐⭐⭐ 매우 자연스러움 (특히 화자 복제 시)

### 발음 정확도
- **MeloTTS**: ⭐⭐⭐⭐ 정확
- **XTTS v2**: ⭐⭐⭐⭐⭐ 매우 정확

## 서버 포트

- **MeloTTS**: `http://127.0.0.1:8000`
- **XTTS v2**: `http://127.0.0.1:8100`

## 실행 명령어
```bash
# MeloTTS 서버
cd ~/myrepos/melotts
uv run uvicorn tts_server:app --host 0.0.0.0 --port 8000

# XTTS v2 서버
cd ~/myrepos/my_xtts_v2
uv run uvicorn server_tts:app --host 0.0.0.0 --port 8100
```

## 요약

| 항목 | MeloTTS | XTTS v2 |
|------|---------|---------|
| **속도** | 🟢 빠름 | 🟡 느림 |
| **품질** | 🟢 우수 | 🟢 매우 우수 |
| **화자 복제** | 🔴 불가 | 🟢 가능 |
| **하드웨어** | CPU | GPU |
| **비용** | 저렴 | 비싸다 |
| **사용 난이도** | 쉬움 | 중간 |

---
