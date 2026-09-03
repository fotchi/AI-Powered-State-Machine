import sys
from flync.model.flync_4_someip.service_interface import SOMEIPEvent, SOMEIPEventgroup
from pydantic import ValidationError

try:
    SOMEIPEvent(id=0),
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)

SOMEIPEventgroup(
    name='EngineEvents',
    id=12345,
    events=[
        SOMEIPEvent(id=0),
        SOMEIPEvent(id=12345, name='EngineOverheat')
    ]
)
print("SUCCESS")
sys.exit(0)