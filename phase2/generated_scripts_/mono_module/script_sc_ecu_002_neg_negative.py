import sys
from pydantic import ValidationError
from flync.model.flync_4_ecu.port import ECUPort

try:
    ecu_port = ECUPort(
        name="eth0",
        mdi_config="BASET1",
        mii_config=None
    )
except ValidationError as e:
    sys.exit(0)

sys.exit(1)