import sys
from flync.model.flync_4_app.app_bindings import AppBindings
from flync.model.flync_4_nm.state_management import GroupTiming
from flync.model.flync_4_app.application import ServiceProviderReference
from flync.model.flync_4_nm.state_management import StateManagementConfig
from flync.model.flync_4_nm.state_management import StateManagementGroup

app_bindings = AppBindings(
    app_refs=["App1", "App2"],
)

group_timing = GroupTiming(
    name="Profile1",
    cycle_time_ms=100,
    sleep={"timeout_ms": 10, "wait_before_sleep_ms": 5},
)

service_provider_reference = ServiceProviderReference(
    type="provider",
    service_name="Service1",
    instance_id=1,
    major_version=1,
)

state_management_config = StateManagementConfig(
    groups=[StateManagementGroup(name="Group1", nm_pdu="PDU1", timing_profile="Profile1")],
    timing_profiles=[group_timing],
)

print("SUCCESS")
sys.exit(0)