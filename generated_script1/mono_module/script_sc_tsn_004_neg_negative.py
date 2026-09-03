import sys
from pydantic import ValidationError
from flync.model.flync_4_tsn.qos import CBSShaper

try:
    cbsshaper = CBSShaper(
        sendSlope=100000000,
        idleSlope=10000000,
        creditBaseTime=0
    )
except ValidationError as e:
    print("SUCCESS")
    sys.exit(0)
else:
    print("FAILURE")
    sys.exit(1)