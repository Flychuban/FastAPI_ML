from pydantic import BaseModel

class GeneratePayload(BaseModel):
    topic: str
    
class AnalysePayload(BaseModel):
    content: str