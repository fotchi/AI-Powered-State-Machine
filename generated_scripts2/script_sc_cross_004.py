import sys
from flync.model.flync_4_app.app_bindings import AppBindings
from flync.model.flync_4_ecu.controller import Controller
from flync.model.flync_4_metadata.metadata import ECUMetadata
from flync.model.flync_4_metadata.metadata import EmbeddedMetadata
from pydantic import ValidationError

try:
    ecu_metadata = ECUMetadata(
        type="ecu",
        compatible_flync_version={"major": 1, "minor": 0, "patch": 0},
        target_system="AARCH"
    )

    controller_metadata = EmbeddedMetadata(
        type="Controller",
        author="N/A",
        compatible_flync_version={"major": 1, "minor": 0, "patch": 0},
        target_system="AARCH",
        app=ecu_metadata
    )

    controller = Controller(
        name="controller1",
        controller_metadata=controller_metadata,
        app_bindings=AppBindings(app_refs=["app1"]),
        ethernet_interfaces=[],
        can_interfaces=[],
        lin_interfaces=[],
        virtual_switch=None
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