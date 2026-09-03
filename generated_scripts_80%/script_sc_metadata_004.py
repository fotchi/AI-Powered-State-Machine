import sys
from flync.model.flync_4_metadata.metadata import HardwareBaseMetadata
from pydantic import ValidationError

try:
    obj = HardwareBaseMetadata(version='v1')
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)