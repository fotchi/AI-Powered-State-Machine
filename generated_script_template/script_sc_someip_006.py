import sys
from pydantic import ValidationError

from flync.model.flync_4_someip.service_interface import SOMEIPEvent
from flync.model.flync_4_someip.service_interface import SOMEIPEventgroup

try:
    someip_event = SOMEIPEvent(
        name="demo_name",
        id=1,
    )
    someip_eventgroup = SOMEIPEventgroup(
        name="demo_name",
        id=1,
        events=[],
    )
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
except Exception as exc:
    print(f"UNEXPECTED ERROR: {type(exc).__name__}: {exc}")
    sys.exit(1)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)
