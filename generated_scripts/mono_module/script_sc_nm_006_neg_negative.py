import sys
from pydantic import ValidationError
from flync.model.flync_4_ecu.controller import Controller
from flync.model.flync_4_nm.state_management import StateMembershipRef
from flync.model.flync_4_ecu.switch import Switch

try:
    controller = Controller(
        name="example_controller",
        controller_metadata={},
        state_memberships=[
            StateMembershipRef(
                group="example_group",
                role="observer",
                relevance_bits=["Diagnostics", "OnlineCommunication"]
            )
        ]
    )
except ValidationError as e:
    sys.exit(0)

print("SUCCESS")
sys.exit(0)