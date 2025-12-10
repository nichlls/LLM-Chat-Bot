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

# TODO: Allow user to provide prompt and type
# TODO: Improve prompt
vehicle_category = "logistics"
prompt = f"List cars below 150 per day for {vehicle_category}"

# Setup bedrock
client = boto3.client("bedrock-agent-runtime", region_name=REGION)

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

    answer = response["output"]["text"]

except Exception as e:
    print(f"Error: {str(e)}")


print(answer)
