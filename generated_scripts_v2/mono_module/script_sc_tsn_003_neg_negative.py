import sys
from flync.model.flync_4_tsn.qos import ATSInstance
from pydantic import ValidationError

try:
    ats_instance = ATSInstance(
        committed_information_rate=1000000,
        committed_burst_size=1000,
        max_residence_time=1000,
        cycleTime=10000000,
        offsetTime=0,
        guardBand=20000000
    )
except ValidationError as e:
    sys.exit(0)

sys.exit(1)