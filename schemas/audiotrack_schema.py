from typing import List, Optional
from pydantic import BaseModel


class AudiotrackBase(BaseModel):
    name: str
    audio_path: str
    loop: bool
    random: bool
    audioboard_id: str


class AudiotrackCreate(AudiotrackBase):
    track_id: int


class AudiotrackUpdate(AudiotrackBase):
    name: Optional[str] = None
    audio_path: Optional[str] = None
    loop: Optional[bool] = None
    random: Optional[bool] = None
    audioboard_id: Optional[str] = None

    class Config:
        from_attributes = True


class Audiotrack(AudiotrackBase):
    track_id: int

    class Config:
        from_attributes = True
