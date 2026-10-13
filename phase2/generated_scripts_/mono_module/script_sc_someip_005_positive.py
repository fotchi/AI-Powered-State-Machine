import sys

from flync.model.flync_4_someip.service_interface import SOMEIPFireAndForgetMethod

someip_fire_and_forget_method = SOMEIPFireAndForgetMethod(
    name="demo_name",
    type='request_response',
    id=1,
)

print("SUCCESS")
sys.exit(0)
