import sys
from flync.model.flync_4_ecu.controller import Controller
from pydantic import ValidationError

scenario = {
    'type': 'Negative',
    'description': 'ECU missing mandatory controllers directory'
}

try:
    controller = Controller(
        name="my_controller",
        controller_metadata={"metadata": "value"},
        ethernet_interfaces=[],
        can_interfaces=[],
        lin_interfaces=[],
        virtual_switch=None,
        app_bindings=None,
        state_memberships=[]
    )
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)