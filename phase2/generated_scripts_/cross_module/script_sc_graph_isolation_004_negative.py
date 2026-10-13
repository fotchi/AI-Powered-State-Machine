import sys
from pydantic import ValidationError
from flync.model.flync_4_app.application import ServiceConsumerReference
from flync.model.flync_4_nm.state_management import StateManagementGroup
try:
    smg = StateManagementGroup(name='group1', nm_pdu='pdu1', timing_profile='profile1')
    obj = ServiceConsumerReference(service_id='nm_group_body_domain', instance_id=1, major_version=1)
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
except Exception as exc:
    print(f"UNEXPECTED ERROR: {type(exc).__name__}: {exc}")
    sys.exit(1)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)