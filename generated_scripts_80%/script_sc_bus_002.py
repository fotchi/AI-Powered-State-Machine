import sys
from pydantic import ValidationError

class Bus:
    def __init__(self, name: str):
        self.name = name

try:
    bus1 = Bus("CAN Bus 1")
    bus2 = Bus("CAN Bus 1") # duplicate bus name
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)