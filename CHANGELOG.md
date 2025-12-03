# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.3.0] - 2025-12-03

### Added

- **🎨 Experimental Mode**: Toggle ON/OFF for advanced features
  - Audio playback for STT input and TTS output
  - Waveform visualization
  - Spectrogram visualization
  - ZIP export (audio + graphs)
  
- **🔊 gTTS Integration**: Default TTS (no server required)
  - 18 languages support
  - 0.5s generation speed
  - Internet connection only
  
- **🎤 Google SR Integration**: Default STT (no server required)
  - 120+ languages support
  - 0.8s recognition speed
  - Internet connection only
  
- **📊 Audio Visualization**:
  - Waveform graph generation (time domain)
  - Spectrogram graph generation (frequency domain)
  - PNG export for both visualizations
  
- **💾 Save & Show Graphs Button**:
  - Automatic graph display after save
  - Download button with filename preview
  - No UI refresh after button click
  
- **📈 Chat History Audio Storage**:
  - STT input audio saved in chat history
  - TTS output audio saved in chat history
  - Audio player for each message
  - Save button for each audio message

### Changed

- **Default Models**:
  - TTS: MeloTTS → **gTTS** (no server required)
  - STT: Whisper → **Google SR** (no server required)
  
- **UI/UX Improvements**:
  - Experimental mode toggle in sidebar
  - Model descriptions and features display
  - Server status indicators (✅ Ready / ❌ Offline)
  
- **File Structure**:
  - Reorganized `api_clients/` into `tts/`, `stt/`, `utils/`
  - Added `audio_processor.py` for audio preprocessing
  - Added `audio_visualizer.py` for visualization

### Fixed

- **🐛 STT Recording Reset Issue**: 
  - Removed `st.rerun()` after STT processing
  - Audio now persists in chat history
  
- **🐛 Save Button UI Refresh**:
  - Removed unnecessary rerun
  - Graphs auto-display after save
  - Download button stays visible
  
- **🐛 File Name Display**:
  - Download button shows filename: `📥 Download: stt_input_20251203_141728.zip`

### Deprecated

- Manual checkbox for showing graphs (replaced with auto-display)

---

## [0.2.0] - 2025-12-02

### Added

- **🎨 Bark TTS Integration**:
  - 100+ voice presets
  - Emotion tokens ([laughs], [sighs], etc.)
  - Music generation capability
  - Speed adjustment (0.5x - 2.0x)
  
- **🎤 F5-TTS Integration**:
  - Zero-shot voice cloning
  - Reference audio support
  - Reference text (optional)
  - Best quality TTS (10-20s)
  
- **🌍 Language Support Expansion**:
  - Added 13 languages total
  - Language-specific model routing
  
- **📊 Model Health Checks**:
  - Server status display
  - Health endpoints for all models
  - Automatic reconnection

### Changed

- Improved Voice Cloning UX:
  - F5-TTS options in sidebar
  - Reference audio management
  - Default fallback (my_voice1.wav)

### Fixed

- F5-TTS reference audio requirement
- Language code routing for all models

---

## [0.1.0] - 2025-12-01

### Added

- **🔊 Initial TTS Models**:
  - MeloTTS (fast multilingual)
  - XTTS v2 (voice cloning)
  
- **🎤 Initial STT Models**:
  - Whisper (high accuracy)
  - Wav2Vec2 (Korean optimized)
  - Vosk (offline)
  
- **🤖 Gemini LLM Integration**:
  - Google Gemini 2.5 Flash
  - Multi-language support
  - Response length control
  
- **🎙️ Core Features**:
  - Voice recording (audiorecorder)
  - Text input
  - Chat history
  - Audio playback
  - Speaker reference recording
  
- **🏗️ Microservice Architecture**:
  - Independent TTS/STT servers
  - HTTP API clients
  - Port-based routing

### Technical

- Built with Streamlit 1.29+
- Python 3.11+ support
- uv package manager
- pydub audio processing

---

## Release Notes

### v0.3.0 - Experimental Mode Release

This release focuses on **audio analysis and research capabilities**:

- ✨ **No server required** to get started (gTTS + Google SR)
- 🧪 **Experimental mode** for audio visualization
- 📊 **Waveform & Spectrogram** generation
- 💾 **ZIP export** for research data collection
- 🎨 Improved UI/UX based on peer review feedback

**Breaking Changes**: None (backward compatible)

**Migration Guide**: 
1. Update `pyproject.toml` (add gtts, matplotlib, librosa, scipy, numpy)
2. Run `uv sync`
3. Reorganize `api_clients/` folder structure (see README)
4. Update imports in `web.py`

---

### v0.2.0 - Multi-Model Expansion

This release adds **Bark** and **F5-TTS** for advanced TTS capabilities:

- 🐶 **Bark**: Emotion & music generation
- 🎵 **F5-TTS**: Best quality voice cloning
- 🌍 13 languages support
- 🔧 Model health monitoring

**Breaking Changes**: None

---

### v0.1.0 - Initial Release

First public release with core functionality:

- Multi-TTS/STT integration
- Gemini LLM integration
- Voice recording & playback
- Microservice architecture

---

## Roadmap

### v0.4.0 (Planned)

- [ ] Real-time streaming (STT + LLM + TTS)
- [ ] Conversation history save/load
- [ ] Voice emotion analysis
- [ ] Multi-speaker conversation

### v0.5.0 (Planned)

- [ ] Docker containerization
- [ ] Cloud deployment (AWS, GCP)
- [ ] API service
- [ ] Web API documentation

### Future

- [ ] StyleTTS2 integration
- [ ] VALL-E integration
- [ ] Seamless M4T integration
- [ ] GPU memory optimization
- [ ] Request caching
- [ ] Batch processing

---

## Contributors

- **Peace Cho** - Initial work - [@chopeacekr](https://github.com/chopeacekr)

See also the list of [contributors](https://github.com/chopeacekr/my-voice-lab/contributors) who participated in this project.

---

[0.3.0]: https://github.com/chopeacekr/my-voice-lab/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/chopeacekr/my-voice-lab/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/chopeacekr/my-voice-lab/releases/tag/v0.1.0