import sys
from flync.model.flync_4_bus.can_bus import CANBus
from flync.model.flync_4_nm.state_management import StateMembershipRef

# Création d'une instance de StateMembershipRef
state_membership = StateMembershipRef(group="group1", role="participant")

# Création d'une instance de CANBus avec la référence à StateMembershipRef
can_bus = CANBus(
    name="can_bus1",
    baud_rate=500000,
    state_memberships=[state_membership]
)

# Validation de l'agrégat
try:
    can_bus.model_dump_json(indent=2)
except ValidationError as e:
    print(e.json(indent=2))
    sys.exit(1)
else:
    print("SUCCESS")
    sys.exit(0)