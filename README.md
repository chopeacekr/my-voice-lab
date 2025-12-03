# 🎙️ My Voice Lab

> **Read this in other languages**: [한국어](./README.ko.md) | [日本語](./README.ja.md)

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.29%2B-red)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Version](https://img.shields.io/badge/Version-0.3.0-orange)](CHANGELOG.md)

> **Multi-TTS/STT Integration System with Experimental Audio Analysis**

Peace Chatbot System that integrates **5 TTS models** and **4 STT models** with advanced audio visualization and analysis capabilities.

![Demo Screenshot](./images/experimental_mode.png)

---

## ✨ Features

- 🎤 **Multi-STT Support** - Google SR, Whisper, Wav2Vec2, Vosk
- 🔊 **Multi-TTS Support** - gTTS, MeloTTS, XTTS v2, F5-TTS, Bark
- 🌍 **13 Languages** - Korean, English, Japanese, Chinese, French, and more
- 🎨 **Voice Cloning** - XTTS v2 & F5-TTS zero-shot voice cloning
- 🧪 **Experimental Mode** - Waveform/Spectrogram visualization + ZIP export
- 🤖 **Gemini LLM Integration** - Natural conversation with Google Gemini
- ⚡ **No Server Required** - Start with gTTS + Google SR (internet only)
- 🏗️ **Microservice Architecture** - 9 independent repositories

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Internet connection (for gTTS & Google SR)

### Installation

```bash
# Clone repository
git clone https://github.com/chopeacekr/my-voice-lab.git
cd my-voice-lab

# Install uv (if not installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync

# Run!
uv run streamlit run web.py
```

Open browser: **http://localhost:8501**

**That's it!** 🎉 No server setup needed.

---

## 📊 Model Comparison

### TTS Models

| Model | Speed | Quality | Server | Voice Cloning | Best For |
|-------|-------|---------|--------|---------------|----------|
| **gTTS** | ⚡⚡⚡ 0.5s | ⭐⭐⭐ | No | ❌ | Quick start |
| **MeloTTS** | ⚡⚡ 1-2s | ⭐⭐⭐⭐ | Yes | ❌ | Real-time |
| **XTTS v2** | ⚡ 5-10s | ⭐⭐⭐⭐⭐ | Yes | ✅ | Voice cloning |
| **F5-TTS** | 10-20s | ⭐⭐⭐⭐⭐ | Yes | ✅ | Best quality |
| **Bark** | 100-200s | ⭐⭐⭐⭐⭐ | Yes | ❌ | Emotion/Music |

### STT Models

| Model | Speed | Accuracy | Server | Offline | Best For |
|-------|-------|----------|--------|---------|----------|
| **Google SR** | ⚡⚡⚡ 0.8s | 85% | No | ❌ | Quick start |
| **Whisper** | ⚡⚡ 1.3s | 90% | Yes | ✅ | Best accuracy |
| **Wav2Vec2** | ⚡⚡ 1.5s | 82% | Yes | ✅ | Korean optimized |
| **Vosk** | ⚡⚡⚡ 0.9s | 78% | Yes | ✅ | Lightweight |

---

## 🎮 Usage

### Basic Usage (No Server)

1. Start the app: `uv run streamlit run web.py`
2. Enter your **GEMINI API Key** in sidebar
3. Select **gTTS** (TTS) and **Google SR** (STT)
4. Click 🎤 to record → Speak → Stop
5. Click **Send** → Get AI response with voice!

### Voice Cloning (XTTS v2)

1. Select **XTTS v2** in TTS Model
2. Click 🎤 in "Record your voice sample"
3. Record 3-5 seconds of your voice
4. Type a message and click **Send**
5. AI responds in **your voice**! 🎉

### Experimental Mode

1. Toggle **🧪 Experimental Mode** ON
2. Record voice → Automatic STT recognition
3. Chat message saved with audio player
4. Click **💾 Save & Show Graphs**
5. Get ZIP file with:
   - Original audio (WAV)
   - Waveform (PNG)
   - Spectrogram (PNG)

---

## 🏗️ Architecture

```
my-voice-lab/
├── web.py                    # Main Streamlit app
├── pyproject.toml           # Dependencies
│
├── api_clients/
│   ├── tts/                 # TTS clients
│   │   ├── gtts_client.py
│   │   ├── melotts_client.py
│   │   ├── xtts_v2_client.py
│   │   ├── f5_client.py
│   │   └── bark_client.py
│   │
│   ├── stt/                 # STT clients
│   │   ├── gSR_client.py
│   │   ├── whisper_client.py
│   │   ├── wav2vec2_client.py
│   │   └── vosk_client.py
│   │
│   └── utils/               # Utilities
│       ├── audio_processor.py
│       └── audio_visualizer.py
│
└── [Independent Repositories]
    ├── my_melotts/          # MeloTTS server (port 8100)
    ├── my_xtts/             # XTTS v2 server (port 8200)
    ├── my_f5/               # F5-TTS server (port 8500)
    ├── my_bark/             # Bark server (port 8600)
    ├── my_whisper/          # Whisper STT (port 8300)
    ├── my_wav2vec2/         # Wav2Vec2 STT (port 8400)
    └── my_vosk/             # Vosk STT (port 8000)
```

**Microservice Architecture**: Each TTS/STT model runs as an independent service with its own repository and server.

---

## 🧪 Experimental Features

### Audio Visualization

Enable **Experimental Mode** to access:

- 🎧 **Audio Playback** - Play recorded STT input & TTS output
- 📊 **Waveform** - Time-domain visualization
- 📈 **Spectrogram** - Frequency-domain analysis
- 💾 **ZIP Export** - Download audio + graphs

### Use Cases

- 🔬 Voice quality analysis
- 📊 Frequency analysis
- 💾 Research data collection
- 🎓 Educational materials

---

## 🛠️ Advanced Setup

### System Dependencies

```bash
# Ubuntu/Debian
sudo apt-get install -y ffmpeg portaudio19-dev

# macOS
brew install ffmpeg portaudio
```

### Install All Models

Each TTS/STT model requires its own server:

```bash
# Clone all repositories
cd ~/myrepos
git clone https://github.com/chopeacekr/my_melotts.git
git clone https://github.com/chopeacekr/my_xtts.git
git clone https://github.com/chopeacekr/my_f5.git
git clone https://github.com/chopeacekr/my_bark.git
git clone https://github.com/chopeacekr/my_whisper.git
git clone https://github.com/chopeacekr/my_wav2vec2.git
git clone https://github.com/chopeacekr/my_vosk.git

# Start each server (in separate terminals)
cd my_melotts && uv run python server_tts.py     # port 8100
cd my_xtts && uv run python server_tts.py        # port 8200
cd my_f5 && uv run python server_tts.py          # port 8500
cd my_bark && uv run python server_tts.py        # port 8600
cd my_whisper && uv run python server_stt.py     # port 8300
cd my_wav2vec2 && uv run python server_stt.py    # port 8400
cd my_vosk && uv run python server_stt.py        # port 8000
```

### System Requirements (Full Setup)

- **RAM**: 16GB+
- **GPU**: NVIDIA 8GB+ (CUDA 11.8+)
- **Disk**: 20GB+

---

## 📚 Documentation

- **[REPORT.md](./REPORT.md)** - Detailed implementation report (Korean)
- **[CHANGELOG.md](./CHANGELOG.md)** - Version history
- **[CONTRIBUTING.md](./CONTRIBUTING.md)** - Contribution guidelines

---

## 🐛 Troubleshooting

### ModuleNotFoundError: gtts_client

**Problem**: File name mismatch (`gTTS_client.py` vs `gtts_client.py`)

**Solution**:
```bash
cd api_clients/tts
mv gTTS_client.py gtts_client.py
```

### gTTS not working

**Problem**: No internet connection or Google TTS API blocked

**Solution**:
- Check internet connection
- Use alternative TTS (MeloTTS)

### Server connection failed

**Problem**: Server not running

**Solution**:
```bash
cd ~/myrepos/my_xtts
uv run python server_tts.py
```

---

## 🤝 Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](./CONTRIBUTING.md) for details.

### Development Setup

```bash
# Fork and clone
git clone https://github.com/chopeacekr/my-voice-lab.git
cd my-voice-lab

# Create branch
git checkout -b feature/amazing-feature

# Install dev dependencies
uv sync --all-extras

# Make changes and test
uv run streamlit run web.py

# Commit and push
git commit -m "Add amazing feature"
git push origin feature/amazing-feature
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

### Models & Libraries

- [gTTS](https://gtts.readthedocs.io/) - Google Text-to-Speech
- [MeloTTS](https://github.com/myshell-ai/MeloTTS) - Fast multilingual TTS
- [Coqui TTS](https://github.com/coqui-ai/TTS) - XTTS v2
- [F5-TTS](https://github.com/SWivid/F5-TTS) - Zero-shot voice cloning
- [Bark](https://github.com/suno-ai/bark) - Expressive TTS
- [Whisper](https://github.com/openai/whisper) - OpenAI STT
- [Wav2Vec2](https://huggingface.co/facebook/wav2vec2-base-960h) - Facebook STT
- [Vosk](https://alphacephei.com/vosk/) - Offline STT

### Frameworks

- [Streamlit](https://streamlit.io/) - Web framework
- [LangChain](https://www.langchain.com/) - LLM integration
- [Google Gemini](https://ai.google.dev/) - LLM
- [librosa](https://librosa.org/) - Audio analysis
- [matplotlib](https://matplotlib.org/) - Visualization

---

## 📞 Contact

**Peace Cho**

- GitHub: [@chopeacekr](https://github.com/chopeacekr)
- Email: chopeaceus@gmail.com
- Project: [https://github.com/chopeacekr/my-voice-lab](https://github.com/chopeacekr/my-voice-lab)

---

## 🌟 Star History

[![Star History Chart](https://api.star-history.com/svg?repos=chopeacekr/my-voice-lab&type=Date)](https://star-history.com/#chopeacekr/my-voice-lab&Date)

---

<div align="center">

**Made with ❤️ by Peace Cho**

[⬆ Back to Top](#-my-voice-lab)

</div>