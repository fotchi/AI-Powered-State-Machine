import sys
from pydantic import ValidationError

from flync.model.flync_4_metadata.metadata import ECUMetadata
from flync.model.flync_4_someip.service_interface import SOMEIPConfig
from flync.model.flync_4_ecu.sockets import Socket
from flync.model.flync_4_metadata.metadata import BaseVersion
from flync.model.flync_4_someip.service_interface import SDConfig
from flync.model.flync_4_someip.service_interface import SOMEIPTimingProfile

try:
    ecu_metadata = ECUMetadata(
        type="demo_type",
        author="demo_author",
        compatible_flync_version=BaseVersion(version="demo_version"),
    )
    someip_config = SOMEIPConfig(
        sd_config=SDConfig(ip_address=None, sd_timings=[]),
        services=[],
        someip_timings=SOMEIPTimingProfile(),
    )
    socket = Socket(
        name="demo_name",
        endpoint_address=None,
        port_no=1,
    )
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
except Exception as exc:
    print(f"UNEXPECTED ERROR: {type(exc).__name__}: {exc}")
    sys.exit(1)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)
