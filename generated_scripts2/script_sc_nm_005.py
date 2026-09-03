import sys
from flync.model.flync_4_nm.state_management import StateMembershipRef

membership = StateMembershipRef(
    group='VEHICLE',
    role='participant',
    relevance_bits=['AutonomousDriving', 'OnlineCommunication']
)

print("SUCCESS")
sys.exit(0)