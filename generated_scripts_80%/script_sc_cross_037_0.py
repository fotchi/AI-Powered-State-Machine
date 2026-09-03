import sys
from flync.model.flync_4_metadata.metadata import ECUMetadata
from flync.model.flync_4_someip.deployment import Layer4Endpoint
from flync.model.flync_4_someip.service_interface import SOMEIPConfig
from pydantic import ValidationError

ecu_metadata = ECUMetadata(
    type='ECU',  # Contrainte violée : type doit être 'ecu'
    author='N/A',
    compatible_flync_version={'major': 1, 'minor': 0},
    extensions=None,
    hardware=None,
    software=None
)

someip_config = SOMEIPConfig(
    version='1.0',
    sd_config=SDConfig(),
    services=[SOMEIPServiceInterface()],
    someip_timings=SOMEIPTimingProfile()
)

layer4_endpoint = Layer4Endpoint(
    protocol='UDP',
    port=12345
)

try:
    ecu_metadata = ECUMetadata(
        type='non_ecu',  # Contrainte violée : type doit être 'ecu'
        author='N/A',
        compatible_flync_version={'major': 1, 'minor': 0},
        extensions=None,
        hardware=None,
        software=None
    )
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)

print("SUCCESS")
sys.exit(0)