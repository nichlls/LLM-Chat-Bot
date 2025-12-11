from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


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
