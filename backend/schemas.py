from pydantic import BaseModel, Field, validator
from typing import Optional


class SchemeBase(BaseModel):
    name: str
    short_description: str
    full_description: str | None = None
    category: str | None = None
    state: str
    min_age: Optional[int] = Field(default=None, ge=0, le=120)
    max_age: Optional[int] = Field(default=None, ge=0, le=120)
    min_income: Optional[int] = Field(default=None, ge=0)
    max_income: Optional[int] = Field(default=None, ge=0)
    occupation: str | None = None
    gender: str | None = None
    caste: str | None = None
    disability: str | None = None
    official_link: str | None = None
    application_process: str | None = None


class SchemeCreate(SchemeBase):
    pass


class SchemeRead(SchemeBase):
    id: int

    class Config:
        from_attributes = True
        orm_mode = True


class UserProfileBase(BaseModel):
    name: str
    state: str
    age: int = Field(..., ge=0, le=120)
    gender: str | None = None
    occupation: str | None = None
    annual_income: Optional[int] = Field(default=None, ge=0)
    caste: str | None = None
    disability: str | None = None


class UserProfileCreate(UserProfileBase):
    pass


class UserProfileRead(UserProfileBase):
    id: int

    class Config:
        from_attributes = True
        orm_mode = True
