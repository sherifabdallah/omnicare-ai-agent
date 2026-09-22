from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str = "healthy"
    version: str
    llm_provider: str
    llm_model: str
