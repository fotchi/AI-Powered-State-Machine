import sys

from flync.model.flync_4_someip.service_interface import SOMEIPParameter
from flync.model.flync_4_someip.service_interface import SOMEIPRequestResponseMethod

someip_parameter = SOMEIPParameter(
    name="demo_name",
    description=None,
    datatype=None,
)
someip_request_response_method = SOMEIPRequestResponseMethod(
    name="demo_name",
    type='request_response',
    id=1,
)

print("SUCCESS")
sys.exit(0)
