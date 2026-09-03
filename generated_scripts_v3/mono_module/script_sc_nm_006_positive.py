import sys

from flync.model.flync_4_ecu.controller import Controller
from flync.model.flync_4_nm.state_management import StateMembershipRef
from flync.model.flync_4_ecu.switch import Switch
from flync.model.flync_4_metadata.metadata import BaseVersion
from flync.model.flync_4_metadata.metadata import EmbeddedMetadata
from flync.model.flync_4_ecu.switch import SwitchConfig

controller = Controller(
    name="demo_name",
    controller_metadata=EmbeddedMetadata(type="demo_type", author="demo_author", compatible_flync_version=BaseVersion(version="demo_version"), target_system="demo_target_system"),
)
state_membership_ref = StateMembershipRef(
    group="demo_group",
)
switch = Switch(
    name="demo_name",
    switch_config=SwitchConfig(meta=EmbeddedMetadata(type="demo_type", author="demo_author", compatible_flync_version=BaseVersion(version="demo_version"), target_system="demo_target_system"), ports=[], vlans=[]),
)

print("SUCCESS")
sys.exit(0)
