import sys
from pydantic import BaseModel, ValidationError

class SystemTopology(BaseModel):
    multicast_path: str = "10.1.1.1"
    vlan_configuration: str = "missing"

try:
    topology = SystemTopology()
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)