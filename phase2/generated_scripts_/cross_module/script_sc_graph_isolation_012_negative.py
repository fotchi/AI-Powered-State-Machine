import sys
from pydantic import ValidationError
from flync.model.flync_4_metadata.metadata import SystemMetadata
try:
    obj = SystemMetadata(type='metadata', author='N/A', compatible_flync_version='1.0.0', release='1.0.0', system_metadata_ref='invalid_ref')
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
except Exception as exc:
    print(f"UNEXPECTED ERROR: {type(exc).__name__}: {exc}")
    sys.exit(1)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)