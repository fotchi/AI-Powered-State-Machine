import sys
from pydantic import ValidationError
from flync.model.flync_4_ecu.controller import Controller

try:
    controller = Controller(
        name="HPC_Controller1",
        controller_metadata={},
        ethernet_interfaces=[],
        can_interfaces=[],
        lin_interfaces=[],
        virtual_switch=None,
        app_bindings=None,
        state_memberships=[]
    )
except ValidationError as e:
    sys.exit(0)

print("SUCCESS")
sys.exit(1)