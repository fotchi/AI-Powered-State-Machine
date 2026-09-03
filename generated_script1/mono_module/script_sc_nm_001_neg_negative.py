import sys
from pydantic import ValidationError
from flync.model.flync_4_nm.state_management import StateManagementGroup

try:
    state_management_group = StateManagementGroup(
        name="VEHICLE",
        nm_pdu="example_nm_pdu",
        timing_profile="nonexistent_profile",
        description="A state management group for a vehicle",
        extensions={"example_extension": "example_value"}
    )
except ValidationError as e:
    print("Validation failed:", e)
    sys.exit(1)

print("SUCCESS")
sys.exit(0)