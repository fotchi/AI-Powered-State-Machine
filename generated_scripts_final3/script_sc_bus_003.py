import sys

from pydantic import BaseModel, IPvAnyAddress

class Metadata(BaseModel):
    id: int = 1
    name: str = "LIN Bus Configuration"

class Interfaces(BaseModel):
    lin_bus: dict[str, any] = {
        "master_node": {"id": 1, "ip_address": IPvAnyAddress("192.168.0.1")},
        "slave_nodes": [{"id": 2, "ip_address": IPvAnyAddress("192.168.0.2")}, {"id": 3, "ip_address": IPvAnyAddress("192.168.0.3")}]
    }

class ScheduleTables(BaseModel):
    table1: dict[str, any] = {
        "frame_id": 1,
        "schedule": [{"node_id": 1, "timestamp": 100}, {"node_id": 2, "timestamp": 200}]
    }
    table2: dict[str, any] = {
        "frame_id": 2,
        "schedule": [{"node_id": 3, "timestamp": 300}, {"node_id": 1, "timestamp": 400}]
    }

class Frames(BaseModel):
    frame1: dict[str, any] = {"id": 1, "name": "Frame 1"}
    frame2: dict[str, any] = {"id": 2, "name": "Frame 2"}

class LINBusConfiguration(BaseModel):
    metadata: Metadata
    interfaces: Interfaces
    schedule_tables: ScheduleTables
    frames: Frames

lin_bus_config = LINBusConfiguration(
    metadata=Metadata(),
    interfaces=Interfaces(),
    schedule_tables=ScheduleTables(),
    frames=Frames()
)

print("SUCCESS")
sys.exit(0)