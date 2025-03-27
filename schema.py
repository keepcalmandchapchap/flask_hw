from pydantic import BaseModel, field_validator

class UpdatePost(BaseModel):
    Title: str | None = None
    Description: str | None = None
    Owner: str | None = None

    @field_validator("Title")
    @classmethod
    def check_title(cls, value: str):
        if len(value) > 16 or value is None:
            return value
        raise ValueError('Title is too short')