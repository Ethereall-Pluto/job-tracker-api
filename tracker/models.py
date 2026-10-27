from datetime import date
from enum import Enum

from pydantic import BaseModel, Field


class Status(str, Enum):
    APPLIED = "applied"
    INTERVIEW = "interview"
    OFFER = "offer"
    REJECTED = "rejected"


class ApplicationCreate(BaseModel):
    company: str = Field(min_length=1)
    position: str = Field(min_length=1)
    source: str = Field(min_length=1, description="Where the vacancy was found, e.g. Djinni")
    applied_on: date


class Application(ApplicationCreate):
    id: int
    status: Status


class StatusUpdate(BaseModel):
    status: Status
