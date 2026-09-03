import sys
from flync.model.flync_4_metadata.metadata import ECUMetadata
from flync.model.flync_4_metadata.metadata import EmbeddedMetadata
from pydantic import ValidationError

try:
    ecu_metadata = ECUMetadata(
        type="ecu",
        author="N/A",
        compatible_flync_version={"major": 1, "minor": 0, "patch": 0},
        extensions={"key": "value"},
        hardware=None,
        software=None
    )

    embedded_metadata = EmbeddedMetadata(
        type="Embedded",
        author="N/A",
        compatible_flync_version={"major": 1, "minor": 0, "patch": 0},
        extensions={"key": "value"},
        hardware=None,
        app=None,
        bootloader=None,
        target_system="AARCH",
        parent_ecu_identifier="HPC_Zone_Left"
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