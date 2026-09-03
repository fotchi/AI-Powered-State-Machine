import sys
from pydantic import ValidationError
from flync.model.flync_4_tsn.qos import HTBInstance

try:
    htb_instance = HTBInstance(
        root_id="0:",
        child_classes=[],
        rate=0,
        burst=1500
    )
except ValidationError as e:
    print("SUCCESS")
    sys.exit(0)
else:
    print("FAILURE")
    sys.exit(1)