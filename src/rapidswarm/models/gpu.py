from typing import Optional

from pydantic import BaseModel, Field, field_validator


class GPU(BaseModel):
    id: str = Field(..., description="Unique identifier for the GPU")
    model: str = Field(..., description="Model name of the GPU")
    memory_size: Optional[int] = Field(
        None, description="Memory size of the GPU in bytes"
    )

    @field_validator("memory_size")
    def validate_memory_size(cls, value):
        if value is not None and value <= 0:
            raise ValueError("memory_size must be a positive integer")
        return value
