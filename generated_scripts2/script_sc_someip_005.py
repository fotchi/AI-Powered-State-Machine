import sys

from flync.model.flync_4_someip.service_interface import SOMEIPEvent

someip_event = SOMEIPEvent(
    name="demo_name",
    id=1,
)

print("SUCCESS")
sys.exit(0)
