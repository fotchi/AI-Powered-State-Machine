import sys
from pydantic import ValidationError

from flync.model.flync_4_ecu.port import ECUPort
from flync.model.flync_4_tsn.timesync import PTPConfig
from flync.model.flync_4_tsn.timesync import PTPPort

try:
    ecu_port = ECUPort(
        name="demo_name",
    )
    ptp_config = PTPConfig(
        ptp_ports=[],
    )
    ptp_port = PTPPort(
        domain_id=1,
        src_port_identity=1,
        sync_config=None,
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
