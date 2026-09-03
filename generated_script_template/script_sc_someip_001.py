import sys

from flync.model.flync_4_someip.service_interface import SOMEIPEvent
from flync.model.flync_4_someip.service_interface import SOMEIPField
from flync.model.flync_4_someip.service_interface import SOMEIPMethod
from flync.model.flync_4_someip.service_interface import SOMEIPServiceInterface
from flync.model.flync_4_metadata.metadata import BaseVersion
from flync.model.flync_4_metadata.metadata import SOMEIPServiceMetadata

someip_event = SOMEIPEvent(
    name="demo_name",
    id=1,
)
someip_field = SOMEIPField(
    name="demo_name",
)
someip_method = SOMEIPMethod(
    name="demo_name",
    type='request_response',
    id=1,
)
someip_service_interface = SOMEIPServiceInterface(
    name="demo_name",
    id=1,
    meta=SOMEIPServiceMetadata(type="demo_type", author="demo_author", compatible_flync_version=BaseVersion(version="demo_version")),
)

print("SUCCESS")
sys.exit(0)
