import json
import re
import logging

logger = logging.getLogger(__name__)


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
        logger.error(f"Error cleaning JSON from LLM: {e}")
        return {
            "status": "error",
            "message": "Failed to parse LLM response",
            "raw_output": llm_response,
        }
