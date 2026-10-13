import sys
from flync.model.flync_4_ecu.controller import Controller
from flync.model.flync_4_metadata.metadata import SystemMetadata
from pydantic import ValidationError
try:
    sys_meta = SystemMetadata(type="example", author="test", compatible_flync_version="1.0.0", release="1.0.0")
    ctrl = Controller(name="Ctrl1", controller_metadata=sys_meta)
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
except Exception as exc:
    print(f"UNEXPECTED ERROR: {type(exc).__name__}: {exc}")
    sys.exit(1)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)