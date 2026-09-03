import sys
from flync.model.flync_4_tsn.qos import Stream

stream = Stream(
    name="01-80-C2-00-00-00-00-01",
    stream_identification=[],
    drop_at_ingress=False,
    max_sdu_size=1500,
    policer=None,
    ipv=None,
    ats=None
)

print("SUCCESS")
sys.exit(0)