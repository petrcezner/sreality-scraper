import datetime
from typing import List

from pydantic import BaseModel


class AdvertisingModel(BaseModel):
    id: int
    title: str
    location: str
    price: str
    living_area: str
    reality_type: str
    building_type: str
    deal_type: str
    images: List[str]
    url: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
