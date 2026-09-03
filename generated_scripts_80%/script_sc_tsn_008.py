import sys
from flync.model.flync_4_tsn.qos import Stream
from pydantic import ValidationError

scenario = {
    'type': 'Negative',
}

stream = Stream(
    name='Test Stream',
    stream_identification=[],
    drop_at_ingress=False,
    max_sdu_size=1522,
    policer=None,
    ipv=7,
    ats=None,
    rate=10e9,  # exceeds the maximum allowed stream rate of 1 Gbps
)

try:
    stream = Stream(
        name='Test Stream',
        stream_identification=[],
        drop_at_ingress=False,
        max_sdu_size=1522,
        policer=None,
        ipv=7,
        ats=None,
        rate=10e9,  # exceeds the maximum allowed stream rate of 1 Gbps
    )
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)