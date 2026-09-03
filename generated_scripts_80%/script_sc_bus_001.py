import sys
from pydantic import BaseModel

class CanBus(BaseModel):
    name: str
    nodes: list[str]
    frames: list[str]

can_bus = CanBus(name="CAN Bus 1", nodes=["Node 1", "Node 2"], frames=["Frame 1", "Frame 2"])
print(can_bus.name)
print("SUCCESS")
sys.exit(0)