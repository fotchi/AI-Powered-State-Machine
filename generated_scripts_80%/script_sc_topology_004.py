import sys
from pydantic import ValidationError

class ECU:
    def __init__(self, ecu_id: str):
        self.ecu_id = ecu_id

class SystemTopology:
    def __init__(self, ECUs: list[ECU]):
        self.ECUs = ECUs

try:
    system_topology = SystemTopology(
        ECUs=[
            ECU(ecu_id="Ecu1"),
            ECU(ecu_id="Ecu2"),  # duplicate identifier
        ]
    )
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)