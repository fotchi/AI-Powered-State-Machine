import sys
from flync.model.flync_4_nm.state_management import StateMembershipRef
from pydantic import BaseModel, Field, List, Optional, Literal, Dict

StateMembershipRef(group="VEHICLE", role="participant", relevance_bits=["AutonomousDriving", "OnlineCommunication"])

print("SUCCESS")
sys.exit(0)