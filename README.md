
<img width="1474" height="738" alt="스크린샷 2025-11-24 235346" src="https://github.com/user-attachments/assets/81b994b5-d669-406a-8b50-134e80e49467" />
유반투 24.04.01, 파이션 3.12 셋팅
# 프로젝트 초기화
```bash
uv init xttsv2
cd xttsv2

# PyTorch CPU 버전 설치
```bash
uv pip install "torch==2.3.1" "torchaudio==2.3.1" --index-url https://download.pytorch.org/whl/cpu

# 핵심 라이브러리
```bash
uv pip install "coqui-tts==0.25.3" "transformers==4.46.2"

# 시스템 패키지
```bash
sudo apt update
sudo apt install ffmpeg -y
sudo apt install -y portaudio19-dev

# 한국어 텍스트 처리 (hangul_romanize)
```bash
uv pip install hangul-romanize

# Streamlit + LangChain + Audio Recorder
```bash
uv pip install streamlit
uv pip install langchain
uv pip install langchain-google-genai
uv pip install streamlit-audiorecorder

# 패키지 리스트 저장
```bash
pip freeze > requirements.txt

# 실행
```bash
uv run streamlit run web.py
