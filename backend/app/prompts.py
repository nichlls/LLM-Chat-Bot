import re


def build_prompt(prompt: str):
    clean_prompt = re.sub(r"[^a-zA-Z0-9 \t\n\r\f\v.,!?;:'\"()—–-]", "", prompt)

    return f"""
    You are a car-rental assistant.

    A customer has provided the following prompt for the car they want:
    {clean_prompt}

    Requirements:
    - Only include vehicles that match or reasonably fit the request.
    - Use only information from the knowledge base.
    - If there are no suitable cars, provide an empty array for "results".
    - Respond only with valid JSON containing a list of suitable vehicles.
    
    If the prompt is not relevant to cars, return an empty "results" field.

    Return JSON in exactly this structure, with the reasoning why a car is a good purchase in the "reasoning" field:

    {{
      "status": "success",
      "query": {{
        "prompt": "{clean_prompt}"
      }},
      "results": [
        {{
          "name": "string",
          "price_per_day": double,
          "seats": int,
          "reasoning": "string"
        }}
      ]
    }}
    
    Make sure that the JSON you are returning is valid, and provide a maximum of 5 in the "results" field. Make sure all data matches the data type in the JSON.
    """
    # Limiting results field prevents truncated JSON by reaching token limit
    # ex. prompt = "any cars" uses more token than available
    # TODO: find a better solution for reaching token limit
