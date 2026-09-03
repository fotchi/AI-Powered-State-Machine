import sys
from flync.model.flync_4_nm.state_management import StateManagementConfig, StateManagementGroup
from flync.model.flync_4_communication.flync_channels import FLYNCChannelConfig
from pydantic import ValidationError

scenario = {
    'type': 'Negative',
}

state_management_config = StateManagementConfig(
    groups=[
        StateManagementGroup(
            name='group1',
            nm_pdu='pdu1',
            timing_profile='profile1'
        )
    ]
)

flync_channel_config = FLYNCChannelConfig(
    pdus=[StandardPDU(type=SignalDataType.UINT16, id=123)],
    can_buses=None,
    lin_buses=None,
    ethernet_pdu_containers=None
)

try:
    obj = StateManagementGroup(
        name='group1',
        nm_pdu=flync_channel_config.pdus[0].id,
        timing_profile='profile1'
    )
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)

class StandardPDU:
    type: SignalDataType
    id: int

class SignalDataType:
    UINT16 = 'UINT16'