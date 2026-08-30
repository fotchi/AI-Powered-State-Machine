import sys
from pydantic import ValidationError

from flync.model.flync_4_tsn.qos import HTBInstance

try:
    htb_instance = HTBInstance(
        root_id="demo_root_id",
        child_classes=[],
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
