import instructor
import boto3
from pydantic import BaseModel
from typing import Type, TypeVar, List, Dict

T = TypeVar("T", bound=BaseModel)

def get_json_from_llm(
    schema: Type[T],
    prompts: List[Dict[str, str]],
    modelId: str = "arn:aws:bedrock:us-east-2:086134439114:inference-profile/us.anthropic.claude-3-5-sonnet-20241022-v2:0",
    temperature: float = 0.1
) -> dict:
    """
    Generic function to generate structured JSON output from Bedrock using instructor.

    Args:
        schema (Type[T]): Pydantic model class for expected output.
        prompts (List[Dict[str, str]]): List of messages in Bedrock chat format:
                                        [{"role": "system", "content": "..."}, {"role": "user", "content": "..."}]
        modelId (str): The Bedrock model ARN.
        temperature (float): Sampling temperature.

    Returns:
        dict: Parsed data as a dictionary.
    """
    # Create Bedrock client and wrap with instructor
    boto_client = boto3.client("bedrock-runtime", region_name="us-east-2")
    client = instructor.from_bedrock(boto_client)

    # Generate structured output directly into Pydantic schema
    response = client.chat.completions.create(
        modelId=modelId,
        temperature=temperature,
        messages=prompts,
        response_model=schema
    )

    return response.dict()
