import logging
from fastapi import Depends, FastAPI, HTTPException
from app.config import get_settings
from app.dependencies import bedrock_client
from app.models.models import RecommendationsResponse, Settings
from app.prompts import build_prompt
from app.utils import clean_llm_response


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Setup FastAPI
app = FastAPI()


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
