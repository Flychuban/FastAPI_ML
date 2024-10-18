from pydantic import BaseModel


# Data Validation Model
class LyricsPayload(BaseModel):
    lyrics: str
