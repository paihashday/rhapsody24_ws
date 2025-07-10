from typing import List, Optional
from pydantic import BaseModel


class ServoboardBase(BaseModel):
    name: str
    ip_address: str
    current_animation: str
    project_id: int

class ServoboardSchemaCreate(BaseModel):
    id: str


class ServoboardSchemaUpdate(BaseModel):
    name: Optional[str]
    ip_address: Optional[str]
    current_animation: Optional[str]

    class Config:
        from_attribute = True


class Servoboard(ServoboardBase):
    id: str

    class Config:
        from_attribute = True