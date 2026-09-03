import sys

from flync.model.flync_4_app.app_bindings import AppBindings
from flync.model.flync_4_bus.can_bus import CANBus
from flync.model.flync_4_ecu.controller import Controller
from flync.model.flync_4_app.application import ServiceProviderReference
from flync.model.flync_4_metadata.metadata import BaseVersion
from flync.model.flync_4_metadata.metadata import EmbeddedMetadata

app_bindings = AppBindings(
)
can_bus = CANBus(
    name="demo_name",
    baud_rate=1,
)
controller = Controller(
    name="demo_name",
    controller_metadata=EmbeddedMetadata(type="demo_type", author="demo_author", compatible_flync_version=BaseVersion(version="demo_version"), target_system="demo_target_system"),
)
service_provider_reference = ServiceProviderReference(
    instance_id=1,
    major_version=1,
)

print("SUCCESS")
sys.exit(0)
