# Bedrock client
import boto3
from fastapi import Depends, HTTPException
from app.config import get_settings
from app.models.models import Settings


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
