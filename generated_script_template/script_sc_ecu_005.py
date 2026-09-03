import sys

from flync.model.flync_4_ecu.controller import VirtualSwitch
from flync.model.flync_4_ecu.controller import VirtualSwitchPort

virtual_switch = VirtualSwitch(
    name="demo_name",
    ports=[],
    vlans=[],
)
virtual_switch_port = VirtualSwitchPort(
    name="demo_name",
    node_connected="demo_node_connected",
)

print("SUCCESS")
sys.exit(0)
