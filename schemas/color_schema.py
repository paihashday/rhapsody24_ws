from typing import List, Optional
from pydantic import BaseModel


class ColorBase(BaseModel):
    name: str
    red_value: int
    green_value: int
    blue_value: int
    white_value: Optional[int] = None


class ColorCreate(ColorBase):
    pass


class ColorUpdate(ColorBase):
    name: Optional[str] = None
    red_value: Optional[int] = None
    green_value: Optional[int] = None
    blue_value: Optional[int] = None
    white_value: Optional[int] = None

    class Config:
        from_attributes = True


class Color(ColorBase):
    id: int

    class Config:
        from_attributes = True