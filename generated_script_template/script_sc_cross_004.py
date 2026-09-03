import sys
from pydantic import ValidationError

from flync.model.flync_4_app.app_bindings import AppBindings
from flync.model.flync_4_ecu.controller import Controller
from flync.model.flync_4_metadata.metadata import ECUMetadata
from flync.model.flync_4_metadata.metadata import EmbeddedMetadata
from flync.model.flync_4_metadata.metadata import BaseVersion

try:
    app_bindings = AppBindings(
    )
    controller = Controller(
        name="demo_name",
        controller_metadata=EmbeddedMetadata(type="demo_type", author="demo_author", compatible_flync_version=BaseVersion(version="demo_version"), target_system="demo_target_system"),
    )
    ecu_metadata = ECUMetadata(
        type="demo_type",
        author="demo_author",
        compatible_flync_version=BaseVersion(version="demo_version"),
    )
    embedded_metadata = EmbeddedMetadata(
        type="demo_type",
        author="demo_author",
        compatible_flync_version=BaseVersion(version="demo_version"),
        target_system="demo_target_system",
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
