import sys
from flync.model.flync_4_tsn.qos import Stream
from pydantic import ValidationError

try:
    stream = Stream(
        name="example_stream",
        stream_identification=[],
        drop_at_ingress=False,
        max_sdu_size=1522,
        policer=None,
        ipv=None,
        ats=None,
        streamId="ZZ-80-C2-00-00-00-00-01"
    )
except ValidationError as e:
    sys.exit(0)

sys.exit(1)