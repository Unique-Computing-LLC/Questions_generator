from duaa_edtools.slide_layouts.layouts import SLIDE_LAYOUTS
from .system_prompt import SYSTEM_PROMPT
from .llm_response_models import SlideData
from src.openai_utils.prompts import LECTURE_SLIDES_PROMPT
from src.openai_utils.llm import get_json_from_llm
import json

# def generate_lecture_slides_metadata(
#     teacher_guidelines: str,
#     lesson_content: str,
#     class_name: str,
#     lesson_name: str,
# ) -> dict:
#     """
#     Sends teacher_guidelines and lesson_content to OpenAI and returns lecture slide content in JSON format.
#     """

#     system_prompt = SYSTEM_PROMPT.format(class_name=class_name, lesson_name=lesson_name, layout_templates=json.dumps(SLIDE_LAYOUTS))
#     user_prompt = (
#         f"{LECTURE_SLIDES_PROMPT.format(teacher_guidelines=teacher_guidelines)}\n\n"
#     )

#     client = OpenAI()

#     response = client.responses.create(
#         model="gpt-4.1",
#         input=[
#             {"role": "system", "content": system_prompt},
#             {"role": "user", "content": user_prompt}
#         ],
#         temperature=0.1,
#         # max_tokens=1500,
#         # response_format = "json"
#     )

#     response.output_text

#     try:
#         slides_json = json.loads(response.output_text)
#     except Exception:
#         # If the model returns markdown or code block, try to extract JSON
#         import re
#         match = re.search(r'```json(.*?)```', response.output_text, re.DOTALL)
#         if match:
#             slides_json = json.loads(match.group(1).strip())
#         else:
#             slides_json = {}
#     return slides_json


# import json
# import re
# import boto3
# from instructor import from_bedrock
# from typing import List


def generate_lecture_slides_metadata(
    teacher_guidelines: str,
    lesson_content: str,
    class_name: str,
    lesson_name: str,
) -> dict:
    """
    Sends teacher_guidelines and lesson_content to LLM via get_json_from_llm
    and returns lecture slide content in structured JSON format.
    """
    system_prompt = SYSTEM_PROMPT.format(
        class_name=class_name,
        lesson_name=lesson_name,
        layout_templates=json.dumps(SLIDE_LAYOUTS),
    )
    user_prompt = LECTURE_SLIDES_PROMPT.format(teacher_guidelines=teacher_guidelines)

    prompts = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]
    modelId="arn:aws:bedrock:us-east-2:086134439114:inference-profile/us.anthropic.claude-3-5-sonnet-20241022-v2:0"
    return get_json_from_llm(SlideData, prompts, modelId)