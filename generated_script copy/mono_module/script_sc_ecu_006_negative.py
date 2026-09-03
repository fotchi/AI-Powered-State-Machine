import sys
from flync.model.flync_4_ecu.port import ECUPort
from pydantic import ValidationError

try:
    ecu_port = ECUPort(
        name="example",
        external_phy=True,
        mdi_config="BASET1",
        mii_config=None
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