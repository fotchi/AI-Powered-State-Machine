import sys
from flync.model.flync_4_tsn.timesync import PTPPort, PTPTimeTransmitterConfig
from pydantic import ValidationError
try:
    sync_cfg = PTPTimeTransmitterConfig(portAdminState='ENABLED', logAnnounceInterval=-130, logSyncInterval=-4)
    obj = PTPPort(domain_id=0, src_port_identity=1, sync_config=sync_cfg)
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
except Exception as exc:
    print(f"UNEXPECTED ERROR: {type(exc).__name__}: {exc}")
    sys.exit(1)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)