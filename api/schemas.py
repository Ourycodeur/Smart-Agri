from pydantic import BaseModel

class PredictionRequest(BaseModel):

    area: str
    year: int
    average_rain_fall_mm_per_year: float
    avg_temp: float
    pesticides_tonnes: float
    item: str
    
class RecommendationRequest(BaseModel):

    area: str
    year: int
    average_rain_fall_mm_per_year: float
    avg_temp: float
    pesticides_tonnes: float