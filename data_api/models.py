from datetime import datetime
from enum import Enum
from typing import List

from pydantic import BaseModel, Field, Json, PositiveInt


class SubmitModel(BaseModel):
    v: PositiveInt = Field(..., alias='_v', description="Version")
    timestamp: datetime = Field(..., alias='_timestamp', description="Timestamp (UNIX Epoch)")
    country: str = Field(..., description="Country Code")
    court: str = Field(..., description="Court code")
    year: int = Field(..., description="Year")
    identifier: str = Field(..., description="Decision identifier")
    text: str = Field(..., description="Content of document")
    user: str = Field(..., description="User key")

    class Config:
        schema_extra = {
            'example': {
                '_v': 1,
                '_timestamp': 1239120938,
                'country': 'BE',
                'court': 'RSCE',
                'year': '2010',
                'identifer': '999.999',
                'text': 'Lorem Ipsum ...',
                'user': 'OIJAS-OIQWE',
            }}
