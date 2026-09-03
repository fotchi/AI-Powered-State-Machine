import sys
from pydantic import ValidationError
from flync.model.flync_4_someip.service_interface import SOMEIPConfig, SDConfig, SOMEIPServiceInterface, SOMEIPTimingProfile

try:
    config = SOMEIPConfig(
        sd_config=SDConfig(),
        services=[SOMEIPServiceInterface()],
        someip_timings=SOMEIPTimingProfile()
    )
except ValidationError as e:
    print("SUCCESS")
    sys.exit(0)
else:
    print("FAILURE")
    sys.exit(1)