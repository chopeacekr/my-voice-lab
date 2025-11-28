from TTS.api import TTS
import torch

device = "cuda" if torch.cuda.is_available() else "cpu"
print("device:", device)

tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)
print("XTTS v2 loaded")

tts.tts_to_file(
    text="이 음성은 제 목소리를 클로닝해서 만든 테스트입니다.",
    file_path="clone_output.wav",
    speaker_wav="my_voice1.wav",
    language="ko",
)