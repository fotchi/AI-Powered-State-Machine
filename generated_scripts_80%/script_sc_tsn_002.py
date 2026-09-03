import sys
from flync.model.flync_4_tsn.timesync import PTPPort, PTPTimeTransmitterConfig, PTPTimeReceiverConfig
from pydantic import ValidationError

try:
    obj = PTPPort(
        domain_id=1,
        src_port_identity=2,
        sync_config=PTPTimeTransmitterConfig(),
        pdelay_config=None,
        port_number=70000
    )
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)