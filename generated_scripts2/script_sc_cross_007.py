import sys

from flync.model.flync_4_app.app_bindings import AppBindings
from flync.model.flync_4_app.application import ServiceProviderReference
from flync.model.flync_4_signal.signal import Signal
from flync.model.flync_4_signal.signal import SignalInstance
from flync.model.flync_4_signal.signal import SignalDataType

app_bindings = AppBindings(
)
service_provider_reference = ServiceProviderReference(
    instance_id=1,
    major_version=1,
)
signal = Signal(
    name="demo_name",
    bit_length=1,
    data_type=SignalDataType.UINT8,
)
signal_instance = SignalInstance(
    signal=Signal(name="demo_name", bit_length=1, data_type=SignalDataType.UINT8),
)

print("SUCCESS")
sys.exit(0)
