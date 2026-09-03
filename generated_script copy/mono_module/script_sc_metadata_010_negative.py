import sys
from flync.model.flync_4_metadata.metadata import ECUMetadata
from pydantic import ValidationError

try:
    obj = ECUMetadata(identifier=None)
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
except Exception as exc:
    print(f"UNEXPECTED ERROR: {type(exc).__name__}: {exc}")
    sys.exit(1)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)