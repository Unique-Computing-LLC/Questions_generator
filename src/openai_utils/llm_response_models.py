from typing import List
from pydantic import BaseModel, Field

class Zone(BaseModel):
    zone_id: str = Field(..., description="Zone ID from the selected layout template.")
    html: str = Field(..., description="Valid HTML content for this zone. Must follow Islamic alignment, simple structure, no inline styles.")

class Image(BaseModel):
    prompt: str = Field(..., description="Friendly image description for DALL·E or other generators, e.g., 'Duaa smiling while holding a plant'.")
    zone_id: str = Field(..., description="Zone ID where this image should appear.")

class Slide(BaseModel):
    slide_id: int = Field(..., description="Integer index of this slide, starting from 0.")
    title: str = Field(..., description="Short, clear title for the slide.")
    layout_id: str = Field(..., description="ID of the chosen layout template.")
    images_updated: bool = Field(..., description="True or False. Indicates if images were updated in this refinement. And the image files need regeneration.")
    teacher_narration_updated: bool = Field(..., description="True or False. Indicates if teacher narration was updated in this refinement. And the teacher narration audio file needs to be regenerated.")
    post_slide_narration_updated: bool = Field(..., description="True or False. Indicates if post-slide narration was updated in this refinement. And the post-slide narration audio file needs to be regenerated.")
    zones: List[Zone] = Field(..., description="List of content zones for this slide.")
    images: List[Image] = Field(..., description="List of images with prompts and corresponding zone IDs.")
    teacher_narration: str = Field(..., description="Teacher narration explaining the content warmly, encouraging participation, and reinforcing Islamic morals.")
    questions: List[str] = Field(..., description="2–3 simple, clear questions related to the slide content.")
    post_slide_narration: str = Field(..., description="Brief narration summarizing key points and including Q&A for reinforcement.")

class SlideData(BaseModel):
    class_name: str = Field(..., description="The class this slide belongs to, e.g., 'Kindergarten'.")
    lesson_name: str = Field(..., description="The lesson this slide belongs to, e.g., 'The Importance of Cleanliness'.")
    slides: List[Slide] = Field(..., description="List containing a single slide's metadata in refinement mode.")