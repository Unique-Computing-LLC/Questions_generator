"""
Open edX Question Generation Pipeline
Generates questions from PDF content using AWS Bedrock Claude models
and publishes them to Open edX content libraries.
"""

import os
import logging
import glob
from typing import Dict, Any

from .openai_utils.prompts import QUESTION_GENERATION_PROMPT
from .utils.question_generator import extract_pdf_text, generate_questions_with_bedrock, publish_to_openedx

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_questions_for_openedx(
    course_content_dir: str = None,
    library_id: str = None,
    topic: str = "Course Content",
    num_questions: int = 10,
    aws_region: str = 'us-east-1'
) -> Dict[str, Any]:
    """
    Generate questions from  content and publish to Open edX library.
    
    Args:
        course_content_dir: Path to directory containing PDF files
        library_id: Open edX library ID (e.g., 'lib:myorg:kg1_english_2025')
        topic: Topic/subject for question generation
        num_questions: Number of questions to generate
        aws_region: AWS region for Bedrock
        
    Returns:
        Dict with generation results
    """
    logger.info("Starting Open edX question generation workflow...")
    
    # Configuration from environment variables
    course_content_dir = course_content_dir or os.getenv('COURSE_CONTENT_DIR', './Course Content')
    library_id = library_id or os.getenv('OPENEDX_LIBRARY_ID', 'lib:myorg:kg1_english_2025')
    api_url = os.getenv('OPENEDX_API_URL', 'http://studio.local.openedx.io:8001')
    
    cookies = {
        'csrftoken': os.getenv('CSRF_TOKEN', ''),
        'studio_session_id': os.getenv('STUDIO_SESSION_ID', ''),
        'edx-jwt-cookie-header-payload': os.getenv('JWT_HEADER_PAYLOAD', '')
    }
    
    try:
        # Extract PDF content
        logger.info(f"Extracting content from: {course_content_dir}")
        pdf_files = glob.glob(f"{course_content_dir}/*.pdf")
        content_text = ""
        
        for pdf in pdf_files[:3]:  # Process up to 3 PDF files
            logger.info(f"Processing: {os.path.basename(pdf)}")
            content_text += extract_pdf_text(pdf) + "\n\n"
        
        if not content_text.strip():
            logger.warning("No content extracted from PDFs")
            return {'success': False, 'error': 'No PDF content found'}
        
        logger.info(f"Extracted {len(content_text)} characters from {len(pdf_files)} PDF files")
        
        # Generate questions using AWS Bedrock
        logger.info(f"Generating {num_questions} questions using AWS Bedrock...")
        questions = generate_questions_with_bedrock(
            content_text, topic, QUESTION_GENERATION_PROMPT, 
            num_questions=num_questions, aws_region=aws_region
        )
        
        if not questions:
            logger.warning("No questions generated")
            return {'success': False, 'error': 'Question generation failed'}
        
        logger.info(f"Generated {len(questions)} questions")
        
        # Publish to Open edX
        logger.info(f"Publishing to Open edX library: {library_id}")
        publish_result = publish_to_openedx(library_id, questions, api_url, cookies)
        
        success_count = publish_result['successful']
        logger.info(f"Successfully published {success_count}/{len(questions)} questions")
        
        return {
            'success': True,
            'questions_generated': len(questions),
            'questions_published': success_count,
            'library_id': library_id,
            'api_url': api_url
        }
        
    except Exception as e:
        logger.error(f"Question generation workflow error: {e}")
        return {'success': False, 'error': str(e)}


def main() -> None:
    """Main entry point for question generation."""
    logger.info("Open edX Question Generation Pipeline")
    logger.info("=" * 50)
    
    # Example usage - can be customized based on needs
    result = generate_questions_for_openedx(
        course_content_dir=os.getenv('COURSE_CONTENT_DIR', './Course Content'),
        library_id=os.getenv('OPENEDX_LIBRARY_ID', 'lib:myorg:kg1_english_2025'),
        topic="KG1 English Course",
        num_questions=10,
        aws_region='us-east-1'
    )
    
    if result['success']:
        logger.info("✅ Question generation completed successfully!")
        logger.info(f"📊 Generated: {result['questions_generated']} questions")
        logger.info(f"📤 Published: {result['questions_published']} questions")
        logger.info(f"📚 Library: {result['library_id']}")
    else:
        logger.error(f"❌ Question generation failed: {result['error']}")


if __name__ == "__main__":
    main()