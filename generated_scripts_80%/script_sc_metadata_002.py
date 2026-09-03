import sys
from flync.model.flync_4_metadata.metadata import ECUMetadata
from pydantic import ValidationError

scenario = {
    'type': 'Negative',
    'data': {
        'identifier': 'ECU_A'
    }
}

try:
    metadata1 = ECUMetadata(identifier='ECU_A')
    metadata2 = ECUMetadata(identifier='ECU_A')  # duplicate identifier
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)