import sys
from pydantic import ValidationError

from flync.model.flync_4_ecu.port import ECUPort
from flync.model.flync_4_someip.deployment import Layer4Endpoint
from flync.model.flync_4_someip.service_interface import SOMEIPConfig
from flync.model.flync_4_someip.service_interface import SDConfig
from flync.model.flync_4_someip.service_interface import SOMEIPTimingProfile

try:
    ecu_port = ECUPort(
        name="demo_name",
    )
    layer4_endpoint = Layer4Endpoint(
        port=1,
    )
    someip_config = SOMEIPConfig(
        sd_config=SDConfig(ip_address=None, sd_timings=[]),
        services=[],
        someip_timings=SOMEIPTimingProfile(),
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
