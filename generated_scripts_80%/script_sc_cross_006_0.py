import sys
from flync.model.flync_4_app.app_bindings import AppBindings
from flync.model.flync_4_app.application import ServiceProviderReference
from flync.model.flync_4_signal.signal import Signal, ValueEncoding, SignalDataType

app_bindings = AppBindings(app_refs=["App1", "App2"])
service_provider_reference = ServiceProviderReference(
    type="provider",
    service_name="transport_service",
    instance_id=123,
    major_version=1
)
signal = Signal(
    name="Signal1",
    description=None,
    bit_length=16,
    data_type=SignalDataType.UINT16,
    factor=2.0,
    offset=3.0,
    lower_limit=None,
    upper_limit=None,
    unit=None,
    initial_value=None,
    value_encoding=ValueEncoding.BINARY
)

print("SUCCESS")
sys.exit(0)