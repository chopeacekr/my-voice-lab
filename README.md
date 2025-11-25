유반투 24.04.01, 파이션 3.12 셋팅

명령어,설명
uv init xttsv2,uv 툴을 사용하여 xttsv2 폴더를 생성하고 프로젝트 환경을 초기화합니다.
cd xttsv2,생성된 프로젝트 디렉토리로 이동합니다.

# coqui-tts 특정 버전 강제 재설치 (선택 사항)
!pip install --force-reinstall "coqui-tts==0.25.3"

# CPU 버전 PyTorch와 Torchaudio 설치
# uv는 --index-url 인자를 지원합니다.
uv pip install "torch==2.3.1" "torchaudio==2.3.1" --index-url https://download.pytorch.org/whl/cpu

# 핵심 라이브러리 설치 (충돌 해결된 조합)
uv pip install "coqui-tts==0.25.3" "transformers==4.46.2"

# 시스템 패키지 관리
sudo apt update
sudo apt install ffmpeg -y
sudo apt install -y portaudio19-dev

# 한국어 텍스트 처리를 위한 라이브러리 설치
# (ImportError: Korean requires: hangul_romanize 해결)
uv pip install hangul-romanize


# Streamlit 및 AI 프레임워크 설치
uv pip install streamlit
uv pip install langchain
uv pip install langchain-google-genai
uv pip install streamlit-audiorecorder

# 실행
pip freeze > requirements.txt
uv run streamlit run web.py