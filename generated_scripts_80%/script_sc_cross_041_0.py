import sys
from flync.model.flync_4_signal.signal import Signal
from flync.model.flync_4_signal.signal import SignalInstance
from flync.model.flync_4_nm.state_management import StateManagementGroup
from pydantic import ValidationError, Field

class StateManagementGroup(StateManagementGroup):
    pass

try:
    state_management_group = StateManagementGroup(
        name="Test Group",
        nm_pdu="NM PDU",
        timing_profile="Timing Profile",
        description="Test Description"
    )
    
    signal = Signal(
        name="Test Signal",
        data_type=SignalDataType.FLOAT32,  # Fault injected value
        bit_length=32,
        factor=1.0,
        offset=0.0,
        lower_limit=None,
        upper_limit=None,
        unit=None,
        initial_value=None,
        value_encoding=None
    )
    
    signal_instance = SignalInstance(
        signal=signal
    )
    
    state_management_group.nm_pdu = "NM PDU with invalid signal"
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)