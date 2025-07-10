from typing import List, Optional
from pydantic import BaseModel


class SwitchboardBase(BaseModel):
    name: str
    ip_address: str
    project_id: int

class SwitchboardCreate(SwitchboardBase):
    id: str

class SwitchboardUpdate(SwitchboardBase):
    name: Optional[str]
    ip_address: Optional[str]
    project_id: Optional[int]

    class Config:
        from_attributes = True

class Switchboard(SwitchboardBase):
    id: str

    class Config:
        from_attributes = True