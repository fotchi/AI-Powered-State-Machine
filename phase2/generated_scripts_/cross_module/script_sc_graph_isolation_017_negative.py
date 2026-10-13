import sys
from pydantic import ValidationError
from flync.model.flync_4_tsn.timesync import PTPConfig
try:
    obj = PTPConfig(cmlds_linkport_enabled=True, ptp_ports="invalid")
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
except Exception as exc:
    print(f"UNEXPECTED ERROR: {type(exc).__name__}: {exc}")
    sys.exit(1)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)