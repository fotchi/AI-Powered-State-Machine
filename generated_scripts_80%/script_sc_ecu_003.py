import sys
from flync.model.flync_4_ecu.switch import Switch
from flync.model.flync_4_ecu.controller import VirtualSwitch, VLANEntry, VirtualSwitchPort

switch = Switch(
    name="VirtualSwitch",
    ports=[VirtualSwitchPort(name="vs_port1", node_connected="ECU")],
    vlans=[VLANEntry(vlan_id=10, vlan_name="vlan1")],
    meta={"description": "Virtual switch configuration"}
)

virtual_switch = VirtualSwitch(
    name="VirtualSwitch",
    ports=[switch.ports[0]],
    vlans=[switch.vlans[0]]
)

print("SUCCESS")
sys.exit(0)