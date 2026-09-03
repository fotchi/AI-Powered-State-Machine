import sys
from flync.model.flync_4_nm.state_management import StateManagementGroup
from pydantic import ValidationError

scenario = {
    'type': 'Negative',
    'data': {
        'groups': [
            {'name': 'VEHICLE', 'nm_pdu': 'NM_PDU_1', 'timing_profile': 'PROFILE_1'},
            {'name': 'VEHICLE', 'nm_pdu': 'NM_PDU_2', 'timing_profile': 'PROFILE_2'}
        ]
    }
}

try:
    StateManagementGroup(**scenario['data'])
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)