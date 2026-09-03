import sys
from flync.model.flync_4_ecu.lin_interface import LINFrameRef
from flync.model.flync_4_ecu.lin_interface import LINMasterInterface
from pydantic import ValidationError

scenario = {
    'type': 'Negative',
    'description': 'LINMasterInterface without a LINFrameRef fails validation',
    'result': 'Validation fails with error \'MissingLinFrameRef\' for the LINMasterInterface',
    'fault': 'missing LINFrameRef in LINMasterInterface'
}

try:
    lin_master_interface = LINMasterInterface(
        name='test',
        bus_ref='test_bus',
        lin_protocol='test_protocol',
        p2_min=1.0,
        st_min=1.0
    )
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
except Exception as exc:
    print(f"UNEXPECTED ERROR: {type(exc).__name__}: {exc}")
    sys.exit(1)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)