from pydantic import BaseModel, Field, field_validator


class UpdateProfileRequest(BaseModel):
    full_name: str | None = Field(None, min_length=2, max_length=200)
    bio: str | None = Field(None, max_length=1000)
    hourly_rate: float | None = Field(None, gt=0)

    @field_validator("full_name")
    @classmethod
    def full_name_not_empty(cls, v):
        if v is not None and not v.strip():
            raise ValueError("Full name cannot be empty")
        return v.strip() if v else v