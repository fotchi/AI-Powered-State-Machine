import sys
from pydantic import ValidationError
from flync.model.flync_4_ecu.ecu import ECU
from flync.model.flync_4_ecu.phy import MII

try:
    ecu = ECU(
        name="hpc_controller1",
        type="high performance compute!",
        ports=[],
        controllers=[],
        ecu_metadata={}
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