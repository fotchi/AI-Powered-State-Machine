import sys
from flync.model.flync_4_tsn.qos import ATSInstance

ats_instance = ATSInstance(
    committed_information_rate=10000000,
    committed_burst_size=1000,
    max_residence_time=1000
)

print("SUCCESS")
sys.exit(0)