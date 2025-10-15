"""Question generation using AWS Bedrock Claude"""
import json
import logging
import boto3
import os
from typing import List, Dict, Any
try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

logger = logging.getLogger(__name__)


def extract_pdf_text(pdf_path: str) -> str:
    """Extract text from PDF"""
    if not PyPDF2:
        return ""
    try:
        with open(pdf_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            return '\n\n'.join([page.extract_text() for page in reader.pages])
    except Exception as e:
        logger.error(f"PDF extraction error: {e}")
        return ""


def generate_olx(q: Dict[str, Any]) -> str:
    """Convert question to OLX format"""
    qtype = q.get('question_type', 'single_select')
    text = q.get('question_text', '')
    exp = q.get('explanation', '')
    name = f"{q.get('difficulty', 'medium').title()} - {q.get('blooms_level', 'understand').title()}"
    exp_xml = f'\n  <solution><div class="detailed-solution"><p>Explanation</p><p>{exp}</p></div></solution>' if exp else ''
    
    if qtype == 'single_select':
        # Single select (multiple choice with 1 correct answer)
        choices = '\n'.join([f'      <choice correct="{"true" if i in q.get("correct_answer", [0]) else "false"}">{c.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")}</choice>' 
                            for i, c in enumerate(q.get('choices', []))])
        return f'<problem display_name="{name}"><multiplechoiceresponse><label>{text}</label><choicegroup type="MultipleChoice">\n{choices}\n    </choicegroup></multiplechoiceresponse>{exp_xml}</problem>'
    
    elif qtype == 'multi_select':
        # Multi-select (multiple choice with multiple correct answers)
        choices = '\n'.join([f'      <choice correct="{"true" if i in q.get("correct_answer", []) else "false"}">{c.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")}</choice>' 
                            for i, c in enumerate(q.get('choices', []))])
        return f'<problem display_name="{name}"><choiceresponse><label>{text}</label><checkboxgroup>\n{choices}\n    </checkboxgroup></choiceresponse>{exp_xml}</problem>'
    
    elif qtype == 'dropdown':
        # Dropdown selection
        choices = q.get('choices', [])
        correct_idx = q.get('correct_answer', [0])[0] if q.get('correct_answer') else 0
        correct_answer = choices[correct_idx] if correct_idx < len(choices) else choices[0]
        # Escape quotes in choices
        escaped_choices = [choice.replace('"', '&quot;') for choice in choices]
        options_str = ', '.join([f'"{choice}"' for choice in escaped_choices])
        return f'<problem display_name="{name}"><optionresponse><label>{text}</label><optioninput options="({options_str})" correct="{correct_answer}"/></optionresponse>{exp_xml}</problem>'
    
    elif qtype == 'numerical_input':
        # Numerical input
        ans = q.get('correct_answer', 0)
        if isinstance(ans, list):
            ans = ans[0]
        tol = q.get('tolerance', 0)
        return f'<problem display_name="{name}"><numericalresponse answer="{ans}"><label>{text}</label><formulaequationinput/><responseparam type="tolerance" default="{tol}"/></numericalresponse>{exp_xml}</problem>'
    
    elif qtype == 'text_input':
        # Text input (short answer)
        ans = q.get('correct_answer', [''])[0] if isinstance(q.get('correct_answer'), list) else q.get('correct_answer', '')
        return f'<problem display_name="{name}"><stringresponse answer="{ans}" type="ci"><label>{text}</label><textline size="20"/></stringresponse>{exp_xml}</problem>'
    
    else:
        # Default to single select
        return generate_olx({**q, 'question_type': 'single_select'})


def generate_questions_with_bedrock(content: str, topic: str, prompt_template: str, 
                                   num_questions: int = 5, aws_region: str = 'us-east-1') -> List[Dict[str, Any]]:
    """Generate questions using OpenAI or AWS Bedrock Claude"""
    try:
        from openai import OpenAI
        
        openai_key = os.getenv('OPENAI_API_KEY')
        if openai_key:
            logger.info("Using OpenAI for question generation")
            client = OpenAI(api_key=openai_key)
            
            prompt = prompt_template.format(content=content[:3000], topic=topic, num_questions=num_questions)
            
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            content_text = response.choices[0].message.content
        else:
            logger.info("Using AWS Bedrock for question generation")
            bedrock = boto3.client('bedrock-runtime', region_name=aws_region)
            
            prompt = prompt_template.format(content=content[:3000], topic=topic, num_questions=num_questions)
            
            payload = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 4096,
                "temperature": 0.7,
                "messages": [{"role": "user", "content": prompt}]
            }
            
            model_id = os.getenv('BEDROCK_MODEL_ID', 'anthropic.claude-3-5-sonnet-20240620-v1:0')
            
            response = bedrock.invoke_model(modelId=model_id, body=json.dumps(payload))
            result = json.loads(response['body'].read())
            content_text = result['content'][0]['text']
        
        # Extract JSON
        if '```json' in content_text:
            content_text = content_text.split('```json')[1].split('```')[0].strip()
        elif '```' in content_text:
            content_text = content_text.split('```')[1].split('```')[0].strip()
        
        data = json.loads(content_text)
        questions = data.get('questions', [])
        
        for q in questions:
            q['olx'] = generate_olx(q)
        
        logger.info(f"Generated {len(questions)} questions")
        return [q for q in questions if q.get('olx')]
        
    except Exception as e:
        logger.error(f"Question generation error: {e}")
        return []


def publish_to_openedx(library_id: str, questions: List[Dict[str, Any]], 
                       api_url: str, cookies: Dict[str, str], 
                       collection_key: str = None, day_level: int = 1) -> Dict[str, Any]:
    """Publish questions to Open edX library"""
    import requests
    
    results = {'successful': 0, 'failed': 0, 'blocks': [], 'errors': []}
    headers = {
        'Accept': 'application/json', 
        'Content-Type': 'application/json', 
        'USE-JWT-COOKIE': 'true',
        'X-CSRFToken': cookies.get('csrftoken', ''),
        'Referer': f'{api_url}/',
        'Origin': api_url
    }
    
    for idx, q in enumerate(questions):
        try:
            # Create unique ID with day level
            unique_id = f"day{day_level}_q{idx}_{hash(q['question_text']) % 10000}"
            
            # Create block
            block_resp = requests.post(
                f"{api_url}/api/libraries/v2/{library_id}/blocks/",
                json={"block_type": "problem", "definition_id": unique_id},
                cookies=cookies, headers=headers, timeout=30
            )
            
            if block_resp.status_code in [200, 201]:
                block_id = block_resp.json().get('id')
                logger.info(f"Created block: {block_id}")
                
                # Update OLX
                olx_resp = requests.post(
                    f"{api_url}/api/libraries/v2/blocks/{block_id}/olx/",
                    json={"olx": q['olx']},
                    cookies=cookies, headers=headers, timeout=30
                )
                
                if olx_resp.status_code in [200, 201]:
                    # Add to collection if specified
                    if collection_key:
                        coll_resp = requests.patch(
                            f"{api_url}/api/libraries/v2/blocks/{block_id}/collections/",
                            json={"collections": [collection_key]},
                            cookies=cookies, headers=headers, timeout=30
                        )
                        if coll_resp.status_code in [200, 201]:
                            logger.info(f"Added to collection: {collection_key}")
                    
                    results['successful'] += 1
                    results['blocks'].append(block_id)
                    logger.info(f"Published question {idx+1}: {block_id}")
                else:
                    results['failed'] += 1
                    error_msg = f"OLX update failed: {olx_resp.status_code} - {olx_resp.text[:200]}"
                    results['errors'].append(error_msg)
                    logger.error(error_msg)
            else:
                results['failed'] += 1
                error_msg = f"Block creation failed: {block_resp.status_code} - {block_resp.text[:200]}"
                results['errors'].append(error_msg)
                logger.error(error_msg)
                
        except Exception as e:
            logger.error(f"Publish error for question {idx}: {e}")
            results['failed'] += 1
            results['errors'].append(str(e))
    
    # Publish the library so content is visible
    if results['successful'] > 0:
        try:
            publish_resp = requests.post(
                f"{api_url}/api/libraries/v2/{library_id}/commit/",
                cookies=cookies, headers=headers, timeout=30
            )
            if publish_resp.status_code in [200, 201]:
                logger.info(f"Published library {library_id} - questions now visible")
            else:
                logger.warning(f"Library publish returned: {publish_resp.status_code}")
        except Exception as e:
            logger.error(f"Library publish error: {e}")
    
    return results

