import sys

from flync.model.flync_4_app.app_bindings import AppBindings
from flync.model.flync_4_ecu.controller import Controller
from flync.model.flync_4_nm.state_management import GroupTiming
from flync.model.flync_4_app.application import ServiceProviderReference
from flync.model.flync_4_nm.state_management import StateManagementGroup
from flync.model.flync_4_metadata.metadata import BaseVersion
from flync.model.flync_4_metadata.metadata import EmbeddedMetadata
from flync.model.flync_4_nm.state_management import SleepTiming

app_bindings = AppBindings(
)
controller = Controller(
    name="demo_name",
    controller_metadata=EmbeddedMetadata(type="demo_type", author="demo_author", compatible_flync_version=BaseVersion(version="demo_version"), target_system="demo_target_system"),
)
group_timing = GroupTiming(
    name="demo_name",
    cycle_time_ms=1,
    sleep=SleepTiming(timeout_ms=1, wait_before_sleep_ms=1),
)
service_provider_reference = ServiceProviderReference(
    instance_id=1,
    major_version=1,
)
state_management_group = StateManagementGroup(
    name="demo_name",
    nm_pdu="demo_nm_pdu",
    timing_profile="demo_timing_profile",
)

print("SUCCESS")
sys.exit(0)
