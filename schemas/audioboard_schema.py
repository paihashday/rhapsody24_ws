from typing import List, Optional
from pydantic import BaseModel


class AudioboardBase(BaseModel):
    name: str
    ip_address: str
    api_port: int
    project_id: int

class AudioboardCreate(AudioboardBase):
    id: str

class AudioboardUpdate(AudioboardBase):
    name: Optional[str]
    ip_address: Optional[str]
    api_port: Optional[int]
    project_id: Optional[int]

    class Config:
        from_attributes = True

class Audioboard(AudioboardBase):
    id: str

    class Config:
        from_attributes = True