import sys
from pydantic import BaseModel, IPvAnyAddress

class Metadata(BaseModel):
    name: str

class Interfaces(BaseModel):
    can_bus: Metadata

class Ports(BaseModel):
    can_port: int

class PDUs(BaseModel):
    id: int
    src_node_id: int
    dst_node_id: int

class CANBusConfig(BaseModel):
    interfaces: list[Interfaces]
    ports: list[Ports]
    pdus: list[PDUs]

scenario_type = 'Positive'

if scenario_type == 'Positive':
    can_bus_config = CANBusConfig(
        interfaces=[Interfaces(can_bus=Metadata(name='CAN Bus 1'))],
        ports=[Ports(can_port=0)],
        pdus=[
            PDUs(id=0x123, src_node_id=0x456, dst_node_id=0x789),
            PDUs(id=0x234, src_node_id=0x567, dst_node_id=0x890)
        ]
    )

print("SUCCESS")
sys.exit(0)