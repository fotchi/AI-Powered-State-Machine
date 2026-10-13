import sys
from flync.model.flync_4_app.application import ServiceProviderReference
from flync.model.flync_4_signal.signal import Signal
from flync.model.flync_4_signal.signal import SignalInstance
from pydantic import ValidationError
try:
    signal = Signal(name='EngineSpeed', bit_length=16, data_type='UINT16')
    signal_instance = SignalInstance(signal=signal, bit_position=0)
    sp_ref = ServiceProviderReference(service_id=1, instance_id=1, major_version=1, signal_ref='sig1')
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
except Exception as exc:
    print(f"UNEXPECTED ERROR: {type(exc).__name__}: {exc}")
    sys.exit(1)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)