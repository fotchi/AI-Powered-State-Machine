import sys
from flync.model.flync_4_metadata.metadata import ECUMetadata
from flync.model.flync_4_metadata.metadata import EmbeddedMetadata
from flync.model.flync_4_ecu.controller import Controller
from pydantic import ValidationError

ecu_metadata = ECUMetadata(
    type="ECU",
    compatible_flync_version={"major": 1, "minor": 0},
    identifier="HPC_ECU_01"
)

controller_metadata = EmbeddedMetadata(
    type="Controller",
    author="N/A",
    compatible_flync_version={"major": 1, "minor": 0},
    target_system="AARCH"
)

controller = Controller(
    name="MyController",
    controller_metadata=controller_metadata,
    ethernet_interfaces=[],
    can_interfaces=[],
    lin_interfaces=[],
    virtual_switch=None,
    app_bindings=None,
    state_memberships=[]
)

try:
    obj = ECUMetadata(
        type="ECU",
        compatible_flync_version={"major": 1, "minor": 0},
        identifier="HPC_ECU_99"
    )
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)

print("SUCCESS")
sys.exit(0)