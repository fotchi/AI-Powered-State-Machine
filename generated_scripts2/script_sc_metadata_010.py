import sys
from pydantic import ValidationError
from flync.model.flync_4_metadata.metadata import ECUMetadata

try:
    obj = ECUMetadata(
        type="ecu",
        author="N/A",
        compatible_flync_version={"major": 1, "minor": 0, "patch": 0},
        extensions=None,
        hardware=None,
        software=None
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