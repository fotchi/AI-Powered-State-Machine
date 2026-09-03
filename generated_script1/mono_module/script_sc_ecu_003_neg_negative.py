import sys
from pydantic import ValidationError
from flync.model.flync_4_ecu.controller import Controller

try:
    controller = Controller(
        name="HPC_Controller1",
        controller_metadata={},
        ethernet_interfaces=None,
        can_interfaces=None,
        lin_interfaces=None,
        virtual_switch=None,
        app_bindings=None,
        state_memberships=[]
    )
except ValidationError as e:
    sys.exit(0)
else:
    sys.exit(1)