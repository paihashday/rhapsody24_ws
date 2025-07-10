from pwd import struct_passwd
from typing import Optional
from pydantic import BaseModel

class DHTValues(BaseModel):
    name: str
    ip_address: str
    temperature_c: float
    temperature_f: float
    humidity: float

class DHTBase(BaseModel):
    name: str
    ip_address: str
    project_id: int

class DHTCreate(DHTBase):
    id: str

class DHTUpdate(DHTBase):
    name: Optional[str]
    ip_address: Optional[str]
    project_id: Optional[int]

    class Config:
        from_attributes = True

class DHT(DHTBase):
    id: str

    class Config:
        from_attributes = True



