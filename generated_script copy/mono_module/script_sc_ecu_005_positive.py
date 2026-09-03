import sys
from flync.model.flync_4_ecu.controller import VirtualSwitch
from flync.model.flync_4_ecu.controller import VirtualSwitchPort

vs = VirtualSwitch(
    name="VirtualSwitch",
    ports=[
        VirtualSwitchPort(
            name="Port1",
            node_connected="ECU1"
        ),
        VirtualSwitchPort(
            name="Port2",
            node_connected="ECU2"
        )
    ],
    vlans=[]
)

print("SUCCESS")
sys.exit(0)