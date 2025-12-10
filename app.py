import boto3
import os
from dotenv import load_dotenv

load_dotenv()

REGION = os.getenv("BEDROCK_REGION")
KB_ID = os.getenv("BEDROCK_KB_ID")
MODEL_ARN = os.getenv("BEDROCK_MODEL_ARN")

if not all([REGION, KB_ID, MODEL_ARN]):
    raise RuntimeError(
        "Missing required environment variables: BEDROCK_REGION, BEDROCK_KB_ID, BEDROCK_MODEL_ARN"
    )


# TODO: Capture vehicle category and price per day from user input
def build_prompt(vehicle_category: str, price_per_day: float) -> str:
    """
    Constructs the prompt for the Bedrock API call.

    This prompt instructs the AI car-rental assistant to query the knowledge base
    for vehicles matching the given category and maximum price per day, and to
    return the results in a strict JSON format.

    :param vehicle_category: The desired category of the rental vehicle.
    :type vehicle_category: str
    :param price_per_day: The maximum price the user is willing to pay per day.
    :type price_per_day: float
    :returns: A formatted string containing the full prompt for the Bedrock model.
    :rtype: str
    """

    return f"""
You are a car-rental assistant.

Requirements:
- Vehicle category: "{vehicle_category}"
- Maximum price: {price_per_day} per day
- Only include vehicles that match or reasonably fit the category.
- Use only information from the knowledge base.
- If no results, return an empty array for "results".
- Respond only with valid JSON.

Return JSON in exactly this structure:

{{
  "status": "success",
  "query": {{
    "category": "{vehicle_category}",
    "max_price_per_day": {price_per_day}
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
            },
        },
    )

    answer = response["output"]["text"]

except Exception as e:
    print(f"Error: {str(e)}")


print(answer)
