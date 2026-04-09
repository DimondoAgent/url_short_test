from datetime import datetime

from pydantic import BaseModel, HttpUrl, field_serializer, field_validator, ConfigDict

class URL_from_client(BaseModel):
    url: HttpUrl

    #added validation to ensure that the URL is well-formed and starts with http:// or https://, and also to enforce a maximum length of 2048 characters to prevent excessively long URLs from being processed
    @field_validator('url', mode='before')
    #added mode='before' to ensure that the validation is performed before any type coercion, which allows us to check the raw input string for length and format before it is parsed as an HttpUrl
    @classmethod
    def validate_n_check_url(cls, value: str) -> str:
        if len(value) > 2048:
            raise ValueError('URL must be less than 2048 characters')
        

        if not value.startswith(('http://', 'https://')):
            raise ValueError('URL must start with http:// or https://')
        return value

class URL_response(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    original_url: str
    short_id: str
    clicks: int
    created_at: datetime



class URL_response_statistics(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    short_id: str
    total_clicks: int
    unique_visitors: int
    created_at: datetime

    @field_serializer("created_at")
    def serialize_created_at(self, value: datetime) -> str:
        return value.isoformat()
    
