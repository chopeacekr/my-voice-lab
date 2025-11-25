유반투 24.04.01, 파이션 3.12
uv init xttsv2
cd xttsv2
!pip install --force-reinstall "coqui-tts==0.25.3"
sudo apt update
python3 -m venv xtts_env
source xtts_env/bin/activate

pip install --upgrade pip

pip install "torch==2.3.1" "torchaudio==2.3.1" --index-url https://download.pytorch.org/whl/cpu

# 충돌해결됨 둘다쓸수있는 최고조합
pip install "coqui-tts==0.25.3" "transformers==4.46.2"

sudo apt install ffmpeg -y
sudo apt install -y portaudio19-dev

# ImportError: Korean requires: hangul_romanize
pip install hangul-romanize

uv pip install streamlit
uv pip install langchain
uv pip install langchain-google-genai
pip install streamlit-audiorecorder














uv pip install --force-reinstall "transformers==4.46.2"


pip freeze > requirements.txt
uv run streamlit run web.py