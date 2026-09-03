import sys
from pydantic import ValidationError

from flync.model.flync_4_app.application import App
from flync.model.flync_4_ecu.ecu import ECU

try:
    app = App(
        name="demo_name",
    )
    ecu = ECU(
        name="demo_name",
        controllers=[],
        ecu_metadata=None,
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
