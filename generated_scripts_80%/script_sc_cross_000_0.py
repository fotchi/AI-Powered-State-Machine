import sys
from flync.model.flync_4_app.app_bindings import AppBindings
from flync.model.flync_4_bus.can_bus import CANBus
from flync.model.flync_4_app.application import ServiceProviderReference

app_bindings = AppBindings(
    app_refs=["App1", "App2"]
)

can_bus = CANBus(
    name="CAN Bus",
    baud_rate=1000000,
    fd_enabled=False,
    frames=[
        {"type": "CANFrame", "id": 123, "data": [1, 2, 3]},
        {"type": "CANFDFrame", "id": 456, "data": [4, 5, 6]}
    ]
)

service_provider_reference = ServiceProviderReference(
    type="provider",
    service_name="Service1",
    instance_id=123,
    major_version=1
)

print("SUCCESS")
sys.exit(0)