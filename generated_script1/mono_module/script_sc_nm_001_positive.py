import sys
from flync.model.flync_4_nm.state_management import StateManagementGroup

group = StateManagementGroup(
    name='VEHICLE',
    nm_pdu='PDU_NmMessage',
    timing_profile='standard'
)

print("SUCCESS")
sys.exit(0)