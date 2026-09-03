import sys
from flync.model.flync_4_metadata.metadata import ECUMetadata
from pydantic import ValidationError

try:
    ecu_metadata1 = ECUMetadata(type="ecu", author="N/A", compatible_flync_version={"major": 1, "minor": 0, "patch": 0})
    ecu_metadata2 = ECUMetadata(type="ecu", author="N/A", compatible_flync_version={"major": 1, "minor": 0, "patch": 0})
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)