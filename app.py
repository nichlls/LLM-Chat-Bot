import boto3
import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException

load_dotenv()

REGION = os.getenv("BEDROCK_REGION")
KB_ID = os.getenv("BEDROCK_KB_ID")
MODEL_ARN = os.getenv("BEDROCK_MODEL_ARN")

if not all([REGION, KB_ID, MODEL_ARN]):
    raise RuntimeError(
        "Missing required environment variables: BEDROCK_REGION, BEDROCK_KB_ID, BEDROCK_MODEL_ARN"
    )


def fetch_vehicle_recommendations(vehicle_category: str, price_per_day: float):
    """
    Fetches vehicle recommendations from a knowledge base using a custom prompt.

    :param vehicle_category: The desired category of the rental vehicle.
    :type vehicle_category: str
    :param price_per_day: The maximum price the user is willing to pay per day.
    :type price_per_day: float
    :returns: A string containing the JSON response from the Bedrock service, which includes
              the list of recommended vehicles, or an error message if the call fails.
    :rtype: str
    """

    # Setup bedrock
    client = boto3.client("bedrock-agent-runtime", region_name=REGION)

    prompt = build_prompt(vehicle_category, price_per_day)

    # TODO: Improve handling
    # Call bedrock
    try:
        response = client.retrieve_and_generate(
            input={"text": prompt},
            retrieveAndGenerateConfiguration={
                "type": "KNOWLEDGE_BASE",
                "knowledgeBaseConfiguration": {
                    "knowledgeBaseId": KB_ID,
                    "modelArn": MODEL_ARN,
                },
            },
        )

        try:
            response_text = response["output"]["text"]
            return response_text
        except Exception as e:
            return f"Error: {str(e)}"

    except Exception as e:
        print(f"Error: {str(e)}")


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


@app.get("/")
async def root():
    return {"message": "Hello"}


# handle user request
# inputs: prompt
def build_prompt(prompt: str):
    return f"""
    You are a car-rental assistant.

    A customer has provided the following prompt for the car they want:
    {prompt}

    Requirements:
    - Only include vehicles that match or reasonably fit the request.
    - Use only information from the knowledge base.
    - If no results, return an empty array for "results".
    - Respond only with valid JSON.

    Return JSON in exactly this structure:

    {{
      "status": "success",
      "query": {{
        "prompt": "{prompt}"
      }},
      "results": [
        {{
          "name": "string",
          "price_per_day": number,
          "seats": number,
          "category": "string",
          "description": "string"
        }}
      ]
    }}
    """
