import sys
from pydantic import ValidationError
from flync.model.flync_4_communication.flync_channels import FLYNCChannelConfig
from flync.model.flync_4_metadata.metadata import SystemMetadata
try:
    meta = SystemMetadata(type="Vehicle", author="John Doe", compatible_flync_version="1.0.0", release="1.0.0")
    obj = FLYNCChannelConfig(metadata_reference=meta)
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
except Exception as exc:
    print(f"UNEXPECTED ERROR: {type(exc).__name__}: {exc}")
    sys.exit(1)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)