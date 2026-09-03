import sys
from pydantic import ValidationError

class Metadata:
    def __init__(self):
        self.can_buses = []

class Interfaces:
    pass

class Ports:
    pass

class Connections:
    pass

class CANBus:
    def __init__(self, name: str, id: int):
        self.name = name
        self.id = id

class FLYNCModel:
    def __init__(self):
        self.metadata = Metadata()
        self.interfaces = Interfaces()
        self.ports = Ports()
        self.connections = Connections()

model = FLYNCModel()

try:
    model.metadata.can_buses.append(CANBus("CAN Bus 1", 0x123))
    model.metadata.can_buses.append(CANBus("CAN Bus 1", 0x456)) # duplicate bus name
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)