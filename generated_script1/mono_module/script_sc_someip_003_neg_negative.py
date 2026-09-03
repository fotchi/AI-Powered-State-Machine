import sys
from flync.model.flync_4_someip.service_interface import SOMEIPServiceInterface
from pydantic import ValidationError

try:
    service = SOMEIPServiceInterface(
        name="VehicleStatusDuplicate",
        id=0x1234,
        major_version=0,
        minor_version=0,
        meta={}
    )
except ValidationError as e:
    print("SUCCESS")
    sys.exit(0)
else:
    print("FAILURE")
    sys.exit(1)