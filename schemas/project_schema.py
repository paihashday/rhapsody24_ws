from typing import List, Optional
from pydantic import BaseModel


class ProjectBase(BaseModel):
    name: str
    description: str
    activated: bool

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(ProjectBase):
    name: Optional[str]
    description: Optional[str]
    activated: Optional[bool]

    class Config:
        from_attributes = True

class Project(ProjectBase):
    id: int

    class Config:
        from_attributes = True