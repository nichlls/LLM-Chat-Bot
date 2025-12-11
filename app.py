from functools import lru_cache
import json
import re
import boto3
import logging
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Pydantic models
class VehicleRecommendations(BaseModel):
    name: str
    price_per_day: float
    seats: int
    reasoning: str


class RecommendationsResponse(BaseModel):
    status: str
    query: dict
    results: list[VehicleRecommendations]


class Settings(BaseSettings):
    BEDROCK_REGION: str
    BEDROCK_KB_ID: str
    BEDROCK_MODEL_ARN: str

    model_config = SettingsConfigDict(env_file=".env")


# Only create settings object once
@lru_cache()
def get_settings() -> Settings:
    try:
        return Settings()
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        # Re-raise as a RuntimeError to halt startup if config is missing/invalid
        raise RuntimeError(
            "Application failed to start due to missing environment variables."
        )


# Setup FastAPI
app = FastAPI()


# Bedrock client
def bedrock_client(settings: Settings = Depends(get_settings)):
    try:
        client = boto3.client(
            "bedrock-agent-runtime", region_name=settings.BEDROCK_REGION
        )
        return client
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to initialise AWS Bedrock client {str(e)}"
        )


# TODO: Sanitise prompt
def build_prompt(prompt: str):
    clean_prompt = re.sub(r"[^a-zA-Z0-9 ]", "", prompt)

    return f"""
    You are a car-rental assistant.

    A customer has provided the following prompt for the car they want:
    {clean_prompt}

    Requirements:
    - Only include vehicles that match or reasonably fit the request.
    - Use only information from the knowledge base.
    - If no results, return an empty array for "results".
    - Respond only with valid JSON containing a list of suitable vehicles.

    Return JSON in exactly this structure, with the reasoning why a car is a good purchase in the "reasoning" field:

    {{
      "status": "success",
      "query": {{
        "prompt": "{clean_prompt}"
      }},
      "results": [
        {{
          "name": "string",
          "price_per_day": number,
          "seats": number,
          "reasoning": "string"
        }}
      ]
    }}
    """


def clean_llm_response(llm_response: str) -> dict:
    # Remove markdown blocks to find json
    match = re.search(r"```(json)?\n?(.*?)```", llm_response, re.DOTALL)
    if match:
        json_string = match.group(2)
    else:
        json_string = llm_response

    try:
        clean_response = json.loads(json_string.strip())
        return clean_response
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        return {
            "status": "error",
            "message": "Failed to parse LLM response",
            "raw_output": llm_response,
        }


@app.get("/recommendations", response_model=RecommendationsResponse)
async def get_recommendations(
    prompt: str,
    client=Depends(bedrock_client),
    settings: Settings = Depends(get_settings),
):
    built_prompt = build_prompt(prompt)

    try:
        response = client.retrieve_and_generate(
            input={"text": built_prompt},
            retrieveAndGenerateConfiguration={
                "type": "KNOWLEDGE_BASE",
                "knowledgeBaseConfiguration": {
                    "knowledgeBaseId": settings.BEDROCK_KB_ID,
                    "modelArn": settings.BEDROCK_MODEL_ARN,
                },
            },
        )

        response_text = response["output"]["text"]

    except Exception as e:
        logger.error(f"Unexpected error calling Bedrock: {e}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

    # Clean LLM response
    response_text = clean_llm_response(response_text)
    try:
        valid_response = RecommendationsResponse(**response_text)
        return valid_response
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to validate response: {str(e)}"
        )
