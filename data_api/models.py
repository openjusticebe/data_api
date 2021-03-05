from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, Json, PositiveInt


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class User(BaseModel):
    email: str
    valid: Optional[bool] = True
    username: str
    admin: bool = True


class UserInDB(User):
    hashed_password: str


class ListTypes(str, Enum):
    country = 'country'
    court = 'court'
    year = 'year'
    document = 'document'


class LanguageTypes(str, Enum):
    FR = 'FR'
    NL = 'NL'
    DE = 'DE'


class StatusTypes(str, Enum):
    NEW = 'new'
    PUBLIC = 'public'
    HIDDEN = 'hidden'
    FLAGGED = 'flagged'
    DELETED = 'deleted'


class AppealType(str, Enum):
    nodata = 'nodata'
    yes = 'yes'
    no = 'no'


class DocTypeType(str, Enum):
    eli = 'eli'
    ecli = 'ecli'


class DocLinkType(BaseModel):
    kind: DocTypeType = Field(..., description='Kind')
    link: str = Field(..., description='Link / identifier')
    label: str = Field(..., description='Label')


class SubmitModel(BaseModel):
    v: PositiveInt = Field(..., alias='_v', description="Version")
    timestamp: datetime = Field(..., alias='_timestamp', description="Timestamp (UNIX Epoch)")
    country: str = Field(..., description="Country Code")
    court: str = Field(..., description="Court code")
    year: int = Field(..., description="Year")
    identifier: str = Field(..., description="Decision identifier")
    text: str = Field(..., description="Content of document")
    lang: LanguageTypes = Field(..., description="Document Language")
    appeal: AppealType = Field(..., description="Appeal")
    user_key: str = Field(..., description="User key")
    doc_links: List[DocLinkType] = Field(..., description="Document links")
    labels: list
    meta: Json = None

    class Config:
        schema_extra = {
            'example': {
                '_v': 1,
                '_timestamp': 1239120938,
                'country': 'BE',
                'court': 'RSCE',
                'year': 2010,
                'identifier': '999.999',
                'text': 'Lorem Ipsum ...',
                'lang': 'NL',
                'user_key': 'OIJAS-OIQWE',
                'labels': [],
                'meta': '{}',
            }}


class UpdateModel(BaseModel):
    v: PositiveInt = Field(..., alias='_v', description="Version")
    timestamp: datetime = Field(..., alias='_timestamp', description="Timestamp (UNIX Epoch)")
    country: str = Field(..., description="Country Code")
    court: str = Field(..., description="Court code")
    year: int = Field(..., description="Year")
    identifier: str = Field(..., description="Decision identifier")
    text: str = Field(..., description="Content of document")
    lang: LanguageTypes = Field(..., description="Document Language")
    appeal: AppealType = Field(..., description="Appeal")
    status: StatusTypes = Field(..., description="Status")
    doc_links: List[DocLinkType] = Field(..., description="Document links")
    labels: list
    meta: Json = None

    class Config:
        schema_extra = {
            'example': {
                '_v': 1,
                '_timestamp': 1239120938,
                'country': 'BE',
                'court': 'RSCE',
                'year': 2010,
                'identifier': '999.999',
                'text': 'Lorem Ipsum ...',
                'lang': 'NL',
                'status': 'flagged',
                'labels': [],
                'meta': '{}',
            }}


class ReadModel(BaseModel):
    v: PositiveInt = Field(..., alias='_v', description="Version")
    timestamp: datetime = Field(..., alias='_timestamp', description="Timestamp (UNIX Epoch)")
    ecli: str = Field(..., description="Document ECLI Identifier")

    class Config:
        schema_extra = {
            'example': {
                '_v': 1,
                '_timestamp': 1239120938,
                'ecli': 'ECLI:BE:RSCE:2020:999.999',
            }
        }


class ListModel(BaseModel):
    v: PositiveInt = Field(..., alias='_v', description="Version")
    timestamp: datetime = Field(..., alias='_timestamp', description="Timestamp (UNIX Epoch)")
    level: ListTypes = Field(..., description="Navigation Level")
    data: Json = None

    class Config:
        schema_extra = {
            'example': {
                '_v': 1,
                '_timestamp': 1239120938,
                'level': 'court',
                'data': '{"country":"BE"}',
            }
        }
