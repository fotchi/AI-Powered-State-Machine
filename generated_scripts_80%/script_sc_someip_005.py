import sys
from flync.model.flync_4_someip.service_interface import SOMEIPField, SOMEIPParameter

class VehicleSpeed(SOMEIPField):
    name: str = "VehicleSpeed"
    parameters: list[SOMEIPParameter] = []
    description: str = ""
    notifier_id: int = None
    setter_id: int = None
    getter_id: int = 1
    reliable: bool = False
    someip_timing: str = "field_default"

print("SUCCESS")
sys.exit(0)