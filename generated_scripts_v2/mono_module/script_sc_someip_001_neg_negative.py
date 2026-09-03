import sys
from flync.model.flync_4_someip.service_interface import SOMEIPConfig, SDConfig, SOMEIPServiceInterface, SOMEIPTimingProfile
from pydantic import ValidationError

try:
    config = SOMEIPConfig(
        sd_config=SDConfig(),
        services=[SOMEIPServiceInterface()],
        someip_timings=SOMEIPTimingProfile()
    )
except ValidationError as e:
    sys.exit(0)

sys.exit(1)