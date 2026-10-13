import sys
from pydantic import ValidationError
from flync.model.flync_4_tsn.timesync import PTPConfig
try:
    obj = PTPConfig(role='boundary_clock', priority1=128, priority2=128, domain_number=256, cmlds_linkport_enabled=False, ptp_ports=[])
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
except Exception as exc:
    print(f"UNEXPECTED ERROR: {type(exc).__name__}: {exc}")
    sys.exit(1)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)