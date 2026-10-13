import sys
from flync.model.flync_4_bus.can_bus import CANBus
from flync.model.flync_4_nm.state_management import StateMembershipRef
state_ref = StateMembershipRef(group="GroupA")
bus = CANBus(name="Bus1", baud_rate=500000, state_memberships=[state_ref])
print("SUCCESS")
sys.exit(0)