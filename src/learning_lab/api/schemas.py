from pydantic import BaseModel, ConfigDict, Field


class InferenceRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    pixels: list[float] = Field(min_length=784, max_length=784)
