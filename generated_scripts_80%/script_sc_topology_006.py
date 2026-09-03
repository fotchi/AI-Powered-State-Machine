import sys
from pydantic import BaseModel, validator
from flync import SystemTopology

class SystemTopology(BaseModel):
    ipv4_address: str

    @validator('ipv4_address')
    def ipv4_address_must_be_valid(cls, v):
        parts = v.split('.')
        if len(parts) != 4:
            raise ValueError("Invalid IPv4 address")
        for part in parts:
            if not part.isdigit() or not 0 <= int(part) <= 255:
                raise ValueError("Invalid IPv4 address")
        return v

system_topology = SystemTopology(ipv4_address="192.168.1.1")

print("SUCCESS")
sys.exit(0)