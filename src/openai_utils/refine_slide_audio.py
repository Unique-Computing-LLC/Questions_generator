from duaa_edtools.utils.s3 import fetch_file_from_s3, write_file_to_s3, s3_file_exists


from openai import OpenAI
from src.openai_utils.llm_response_models import AudioRefinementResponse
from .audio_refinement_system_prompt import SYSTEM_PROMPT
from src.openai_utils.prompts import AUDIO_REFINEMENT_PROMPT
from src.openai_utils.llm import get_json_from_llm
import json

def refine_slide_audio(
    event, config
) -> dict:
    """
    Sends teacher_guidelines and lesson_content to LLM and returns refined slide audio content in JSON format.
    """
    s3_slide_metadata_file = config.EVENT_DIR + "/slide_metadata.json"
    slide_metadata_file_path = "/tmp/slide_metadata.json"
    fetch_file_from_s3(s3_slide_metadata_file, slide_metadata_file_path)

    with open(slide_metadata_file_path, "r", encoding="utf-8") as f:
        slide_deck_metadata = json.load(f)

    slide_metadata = slide_deck_metadata['slides'][int(config.SLIDE_NO)]
    system_prompt = SYSTEM_PROMPT.format(class_name=config.CLASS)
    user_prompt = AUDIO_REFINEMENT_PROMPT.format(slide_metadata=slide_metadata, audio_refinement_prompt=config.END_USER_PROMPT)

    prompts = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    slides_json = get_json_from_llm(AudioRefinementResponse, prompts)

    updated_slide_metadata = slide_metadata
    for k in slides_json:
        updated_slide_metadata[k] = slides_json[k]

    updated_slide_deck_metadata = slide_deck_metadata
    updated_slide_deck_metadata['slides'][int(config.SLIDE_NO)] = updated_slide_metadata

    updated_metadata_path = "/tmp/updated_slide_metadata.json"
    with open(updated_metadata_path, "w", encoding="utf-8") as f:
        json.dump(updated_slide_deck_metadata, f, ensure_ascii=False, indent=2)

    write_file_to_s3(updated_metadata_path, s3_slide_metadata_file)
    
    return {
        "SLIDE_NO": config.SLIDE_NO,
        "USER_PROMPT": config.END_USER_PROMPT,
        "UPDATED_SLIDE_METADATA_FILE": s3_slide_metadata_file,
    }