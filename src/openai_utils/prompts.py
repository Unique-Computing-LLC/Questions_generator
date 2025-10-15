LECTURE_SLIDES_PROMPT = (
    "You are an expert educator. Given the following teacher guidelines, "
    "generate a JSON structure suitable for creating lecture slides. "
    "Since theese slides are for little kids of class KG. They should have related content, images, giff etc and less text and large words."
    "Teacher Guidelines:\n"
    "{teacher_guidelines}\n\n"
    "Return only the JSON."
)

COLOR_PALLETTE = """
Light Background: #FFF4ED
Primary Color: #6D3961
Secondary Color: #B3987F
Accent Colors: #FFB173, #896646
"""

AHMED_PROMPT = "A flat-style digital illustration of a young Muslim boy, aged 2.5 to 3 years, with no background, no outlines, and clean, soft color shading. He is wearing a bright long tunic and pants, with shoes. His skin tone is 'porcelain'. He wears a Muslim cap (taqiyah) on his head. The illustration should not have facial features and should follow an Islamic visual style suitable for educational content."

DUAA_PROMPT = "A flat-style digital illustration of a young Muslim girl, aged 2.5 to 3 years, with no background, no outlines, and clean, soft color shading. She is wearing a hijab and a dress, with pants and shoes. Her skin tone is 'porcelain'. The illustration should not have facial features and must follow an Islamic visual style suitable for educational content for children."

IMAGE_PROMPT = (
    "Create a flat-style digital illustration with bright colors and a cartoonish style suitable for young children. "
    "Main image description: {description}\n"
    "The illustration should have following hexa color #FFF4ED as the background, no outlines, flat style."
    "Do not include any text or names in the image. "
) 


AUDIO_REFINEMENT_PROMPT = """
You are an expert educator and curriculum designer. Given the following metadata used to generate lecture slide content for a particular lesson, and the refinement needed in the audio content. Update the JSON with new audio content according to the Audio Refinement Needs specified below.

Lesson Metadata:
{slide_metadata}

Audio Refinement Needs:
{audio_refinement_prompt}
"""

SLIDE_REFINEMENT_PROMPT = """

You are an expert educator and curriculum designer. Given the following metadata used to generate lecture slide content for a particular lesson, and the refinement needed in the slide content. Update the JSON with new slide content according to the Slide Refinement Needs specified below.

You can choose to refine the existing slide content or redesign it completely if asked in the Slide Refinement Needs, based on the provided layout templates.

Lesson Metadata:
{slide_metadata}

Slide Refinement Needs:
{slide_refinement_prompt}

"""

QUESTION_GENERATION_PROMPT = """You are an expert educator creating assessment questions for Open edX.

Course Content:
{content}

Topic: {topic}

Generate {num_questions} diverse questions covering key learning objectives.

Question Types to include (Open edX formats):
- Single select (multiple choice with 1 correct answer)
- Multi-select (multiple choice with multiple correct answers)
- Dropdown (select from dropdown menu)
- Numerical input (enter a number)
- Text input (short text answer)

For each question provide:
1. question_text: Clear, unambiguous question
2. question_type: One of: single_select, multi_select, dropdown, numerical_input, text_input
3. choices: Array of options (for single_select/multi_select/dropdown)
4. correct_answer: Correct answer(s) - index for select types, value for others
5. explanation: Why the answer is correct
6. difficulty: easy/medium/hard
7. blooms_level: remember/understand/apply/analyze/evaluate/create
8. tags: Topic tags array

Return ONLY valid JSON:
{{
  "questions": [
    {{
      "question_text": "What is...",
      "question_type": "single_select",
      "choices": ["Option A", "Option B", "Option C", "Option D"],
      "correct_answer": [1],
      "explanation": "...",
      "difficulty": "medium",
      "blooms_level": "understand",
      "tags": ["{topic}"]
    }}
  ]
}}"""