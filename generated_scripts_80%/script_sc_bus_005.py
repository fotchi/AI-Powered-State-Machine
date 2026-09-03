import sys
from pydantic import BaseModel

class CanBusFrame(BaseModel):
    pdu_ref: str
    payload_size: int

frame = CanBusFrame(pdu_ref="existing_pdu", payload_size=5)
print("SUCCESS")
sys.exit(0)