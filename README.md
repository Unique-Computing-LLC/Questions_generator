# DUAA Lesson Content Generator

An AI-powered question generation system that extracts content from PDF files and generates Open edX-compatible questions using AWS Bedrock Claude models.

## Features

- **PDF Content Extraction**: Automatically extracts text from PDF course materials
- **AI Question Generation**: Uses AWS Bedrock Claude 3.5 Sonnet for intelligent question creation
- **Open edX Integration**: Publishes generated questions directly to Open edX content libraries
- **Multiple Question Types**: Supports single-select, multi-select, dropdown, numerical input, and text input questions
- **Flexible Configuration**: Environment-based configuration for different courses and libraries

## Architecture

### Question Generation Pipeline

```
PDF Content → Text Extraction → AWS Bedrock Claude → Question Generation → Open edX Publishing
```

1. **Content Ingestion**: PDF files are processed and text is extracted
2. **AI Processing**: AWS Bedrock Claude 3.5 Sonnet generates diverse questions based on content
3. **Question Formatting**: Questions are converted to Open edX OLX format
4. **Library Publishing**: Questions are published to specified Open edX content libraries

## AWS Bedrock Integration

This system uses AWS Bedrock's Claude 3.5 Sonnet model (`anthropic.claude-3-5-sonnet-20240620-v1:0`) for question generation. The AI model:

- Analyzes PDF content and learning objectives
- Generates diverse question types appropriate for different cognitive levels
- Creates questions with proper explanations and metadata
- Ensures questions align with Bloom's taxonomy levels

### Supported Question Types

- **Single Select**: Multiple choice with one correct answer
- **Multi-select**: Multiple choice with multiple correct answers  
- **Dropdown**: Selection from dropdown menu
- **Numerical Input**: Number-based answers with tolerance
- **Text Input**: Short text responses

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd duaa-lesson-content-generator
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure AWS credentials:
```bash
# Set AWS credentials for Bedrock access
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-east-1
```

## Configuration

### Environment Variables

```bash
# AWS Bedrock Configuration
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20240620-v1:0

# Open edX Configuration
export OPENEDX_API_URL=http://studio.local.openedx.io:8001
export OPENEDX_LIBRARY_ID=lib:myorg:kg1_english_2025
export CSRF_TOKEN=your_csrf_token
export STUDIO_SESSION_ID=your_session_id
export JWT_HEADER_PAYLOAD=your_jwt_payload

# Content Configuration
export COURSE_CONTENT_DIR=/path/to/course/content
```

### Alternative: OpenAI Fallback

If AWS Bedrock is not available, the system can fallback to OpenAI:

```bash
export OPENAI_API_KEY=your_openai_key
```

## Usage

### Basic Usage

```python
from src.main import generate_questions_for_openedx

# Generate questions from PDF content
result = generate_questions_for_openedx(
    course_content_dir="./Course Content",
    library_id="lib:myorg:kg1_english_2025",
    topic="KG1 English Course",
    num_questions=10,
    aws_region='us-east-1'
)

if result['success']:
    print(f"Generated {result['questions_generated']} questions")
    print(f"Published {result['questions_published']} questions")
```

### Command Line Usage

```bash
python src/main.py
```

### Creating Day-Level Collections

The system supports creating organized question collections for different course days:

```python
from src.utils.openedx_hierarchy import OpenEdXHierarchyManager

# Create day-level collections
manager = OpenEdXHierarchyManager(library_id, api_url, cookies)

for day in range(1, 11):  # Day 1-10
    collection = manager.create_collection(
        f"Day {day} Questions",
        f"Questions for Day {day} content"
    )
    
    # Generate and publish day-specific questions
    questions = generate_questions_with_bedrock(
        day_content, f"Day {day} Content", prompt, num_questions=5
    )
    publish_to_openedx(library_id, questions, api_url, cookies, collection['key'], day)
```

## Project Structure

```
duaa-lesson-content-generator/
├── src/
│   ├── main.py                    # Main entry point
│   ├── openai_utils/
│   │   └── prompts.py            # AI prompts for question generation
│   └── utils/
│       ├── question_generator.py  # Core question generation logic
│       └── openedx_hierarchy.py  # Open edX collection management
├── requirements.txt              # Python dependencies
└── README.md                    # This file
```

## Dependencies

- `boto3`: AWS SDK for Bedrock access
- `openai`: OpenAI API client (fallback)
- `PyPDF2`: PDF text extraction
- `requests`: HTTP client for Open edX API
- `python-dotenv`: Environment variable management

## Open edX Integration

The system integrates with Open edX through the `tutor-contentlibrary-api` plugin:

1. **Authentication**: Uses CSRF tokens and session cookies
2. **Question Publishing**: Creates problem blocks in content libraries
3. **OLX Format**: Generates Open edX-compatible XML question format
4. **Collection Management**: Organizes questions into day-level collections

## Error Handling

The system includes comprehensive error handling for:

- PDF extraction failures
- AWS Bedrock API errors
- Open edX authentication issues
- Network connectivity problems
- Invalid question formats

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:

1. Check the error logs for detailed error messages
2. Verify AWS credentials and permissions
3. Ensure Open edX API access is properly configured
4. Review environment variable settings

## Changelog

### Version 1.0.0
- Initial release with AWS Bedrock integration
- Open edX question publishing
- PDF content extraction
- Multiple question type support
- Day-level collection organization
