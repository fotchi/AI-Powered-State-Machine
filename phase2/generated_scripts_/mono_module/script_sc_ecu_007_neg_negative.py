import sys
from pydantic import ValidationError

from flync.model.flync_4_ecu.switch import Switch
from flync.model.flync_4_ecu.controller import VirtualSwitch
from flync.model.flync_4_ecu.controller import VirtualSwitchPort
from flync.model.flync_4_metadata.metadata import BaseVersion
from flync.model.flync_4_metadata.metadata import EmbeddedMetadata
from flync.model.flync_4_ecu.switch import SwitchConfig

try:
    switch = Switch(
        name="demo_name",
        switch_config=SwitchConfig(meta=EmbeddedMetadata(type="demo_type", author="demo_author", compatible_flync_version=BaseVersion(version="demo_version"), target_system="demo_target_system"), ports=[], vlans=[]),
    )
    virtual_switch = VirtualSwitch(
        name="demo_name",
        ports=[],
        vlans=[],
    )
    virtual_switch_port = VirtualSwitchPort(
        name="demo_name",
        node_connected="demo_node_connected",
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
