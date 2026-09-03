import sys

from flync.model.flync_4_ecu.controller import Controller
from flync.model.flync_4_ecu.switch import Switch
from flync.model.flync_4_ecu.controller import VirtualSwitch
from flync.model.flync_4_ecu.controller import VirtualSwitchPort
from flync.model.flync_4_metadata.metadata import BaseVersion
from flync.model.flync_4_metadata.metadata import EmbeddedMetadata
from flync.model.flync_4_ecu.switch import SwitchConfig

controller = Controller(
    name="demo_name",
    controller_metadata=EmbeddedMetadata(type="demo_type", author="demo_author", compatible_flync_version=BaseVersion(version="demo_version"), target_system="demo_target_system"),
)
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

print("SUCCESS")
sys.exit(0)
