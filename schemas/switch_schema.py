from typing import List, Optional
from pydantic import BaseModel


class SwitchBase(BaseModel):
    name: str
    position: int
    state: bool
    locked: bool
    switchboard_id: str


class SwitchCreate(SwitchBase):
    pass


class SwitchUpdate(SwitchBase):
    name: Optional[str] = None
    position: Optional[int] = None
    state: Optional[bool] = None
    locked: Optional[bool] = None
    switchboard_id: Optional[str] = None

    class Config:
        from_attributes = True


class Switch(SwitchBase):
    id: int

    class Config:
        from_attributes = True


class ToggleSwitchsRequest(BaseModel):
    switchs: dict[int, bool]


class LockSwitchRequest(BaseModel):
    switchs: dict[int, bool]