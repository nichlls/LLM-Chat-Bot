import json
import re
import boto3
import os
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException

load_dotenv()

REGION = os.getenv("BEDROCK_REGION")
KB_ID = os.getenv("BEDROCK_KB_ID")
MODEL_ARN = os.getenv("BEDROCK_MODEL_ARN")

if not all([REGION, KB_ID, MODEL_ARN]):
    raise RuntimeError(
        "Missing required environment variables: BEDROCK_REGION, BEDROCK_KB_ID, BEDROCK_MODEL_ARN"
    )


# Setup FastAPI
app = FastAPI()


# Bedrock client
def bedrock_client():
    try:
        client = boto3.client("bedrock-agent-runtime", region_name=REGION)
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


@app.get("/recommendations")
async def get_recommendations(
    prompt: str,
    client=Depends(bedrock_client),
):
    built_prompt = build_prompt(prompt)

    try:
        response = client.retrieve_and_generate(
            input={"text": built_prompt},
            retrieveAndGenerateConfiguration={
                "type": "KNOWLEDGE_BASE",
                "knowledgeBaseConfiguration": {
                    "knowledgeBaseId": KB_ID,
                    "modelArn": MODEL_ARN,
                },
            },
        )

        response_text = response["output"]["text"]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bedrock API error: {str(e)}")

    # Clean LLM response
    response_text = clean_llm_response(response_text)
    # TODO: Use pydantic for ensuring correct format
    return response_text
