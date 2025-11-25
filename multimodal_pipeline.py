from pathlib import Path
from melotts_client import synth_to_file

# 1. LLM / 텍스트 생성 (여기는 Peace 님이 이미 쓰는 transformers==4.46.2 모델 사용)
def generate_text_from_prompt(prompt: str) -> str:
    # TODO: 실제 LLM 호출로 교체
    # 예시로 그냥 프롬프트를 약간 가공
    return f"{prompt} 에 대한 설명입니다. 오늘도 좋은 하루 되세요."


# 2. 이미지 생성 or 가공 (Stable Diffusion, DALL·E, etc.)
def generate_image_from_prompt(prompt: str, out_path: str = "out_image.png") -> Path:
    # TODO: 실제 이미지 생성 코드로 교체
    # 여기서는 그냥 더미 경로만 반환
    return Path(out_path)


# 3. TTS (MeloTTS 서버 호출)
def generate_tts_from_text(text: str, out_path: str = "out_audio.wav") -> Path:
    return synth_to_file(text, out_path=out_path, lang="KR")


def run_multimodal_pipeline(prompt: str):
    """
    입력: 사용자의 프롬프트(텍스트)
    출력: 생성된 텍스트, 이미지 파일 경로, 오디오 파일 경로
    """
    text = generate_text_from_prompt(prompt)
    image_path = generate_image_from_prompt(prompt, out_path="pipeline_image.png")
    audio_path = generate_tts_from_text(text, out_path="pipeline_audio.wav")
    return {
        "text": text,
        "image_path": image_path,
        "audio_path": audio_path,
    }


if __name__ == "__main__":
    result = run_multimodal_pipeline("강아지가 공원에서 노는 장면")
    print("=== PIPELINE RESULT ===")
    print("TEXT:", result["text"])
    print("IMAGE PATH:", result["image_path"])
    print("AUDIO PATH:", result["audio_path"])
