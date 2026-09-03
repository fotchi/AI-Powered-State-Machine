import sys
from flync.model.flync_4_someip.service_interface import SOMEIPServiceInterface
from flync.model.flync_4_someip.field import SOMEIPField
from flync.model.flync_4_someip.event import SOMEIPEvent
from flync.model.flync_4_someip.method import SOMEIPFireAndForgetMethod, SOMEIPRequestResponseMethod
from flync.model.flync_4_someip.metadata import SOMEIPServiceMetadata

someip_service_interface = SOMEIPServiceInterface(
    name='EngineControl',
    id=4660,
    fields=[SOMEIPField(description='field1')],
    events=[SOMEIPEvent(description='event1')],
    methods=[
        SOMEIPFireAndForgetMethod(name='method1'),
        SOMEIPRequestResponseMethod(name='method2')
    ],
    meta=SOMEIPServiceMetadata()
)

print("SUCCESS")
sys.exit(0)