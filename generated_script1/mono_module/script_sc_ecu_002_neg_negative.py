import sys
from flync.model.flync_4_ecu.port import ECUPort, BASET1, MII
from pydantic import ValidationError

try:
    port = ECUPort(
        name="eth0",
        mdi_config=BASET1(mode="1000baseT"),
        mii_config=None
    )
except ValidationError as e:
    print("SUCCESS")
    sys.exit(0)
else:
    print("FAILURE")
    sys.exit(1)