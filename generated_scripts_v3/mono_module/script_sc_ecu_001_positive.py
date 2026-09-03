import sys

from flync.model.flync_4_ecu.ecu import ECU
from flync.model.flync_4_ecu.port import ECUPort

ecu = ECU(
    name="demo_name",
    controllers=[],
    ecu_metadata=None,
)
ecu_port = ECUPort(
    name="demo_name",
)

print("SUCCESS")
sys.exit(0)
