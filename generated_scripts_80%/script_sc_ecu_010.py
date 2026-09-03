import sys
from flync.model.flync_4_ecu.switch import Switch
from flync.model.flync_4_ecu.controller import VirtualSwitch
from pydantic import ValidationError

switch = Switch(
    name="Switch",
    ports=[],
    vlans=[
        VLANEntry(vlan_id=100, vlan_name="Multicast VLAN")
    ],
    host_controller=None,
    dynamic_address_aging_time=None,
    meta={"author": "John Doe", "date": "2022-01-01"}
)

virtual_switch = VirtualSwitch(
    name="Virtual Switch",
    ports=[],
    vlans=[
        VLANEntry(vlan_id=100, vlan_name="Multicast VLAN")
    ]
)

try:
    switch.validate_unique_port_number()
    virtual_switch.validate_ipv_mapping()
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)