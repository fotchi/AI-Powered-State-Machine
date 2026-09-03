import sys
from flync.model.flync_4_nm.state_management import StateManagementGroup, StateMembershipRef

state_management_group = StateManagementGroup(
    name="VEHICLE",
    nm_pdu="PDU_NmMessage",
    timing_profile="standard"
)

entity1_state_membership_ref = StateMembershipRef(group="VEHICLE", role="participant")
entity2_state_membership_ref = StateMembershipRef(group="VEHICLE", role="observer")

print("SUCCESS")
sys.exit(0)