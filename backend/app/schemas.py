from pydantic import BaseModel, Field

class AnalyzeRequest(BaseModel):
    alert_text : str = Field(..., min_length=1)