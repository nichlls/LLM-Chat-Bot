from functools import lru_cache
import logging
from app.models.models import Settings

logger = logging.getLogger(__name__)


@lru_cache()
def get_settings() -> Settings:
    try:
        return Settings()
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        raise RuntimeError(
            "Application failed to start due to missing environment variables."
        )
