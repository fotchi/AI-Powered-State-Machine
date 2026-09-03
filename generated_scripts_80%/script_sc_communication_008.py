import sys
from pydantic import BaseModel, ValidationError

class TCPOption(BaseModel):
    vlan_id: int = 20

try:
    tcpoption = TCPOption()
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)