import sys

from flync.model.flync_4_tsn.timesync import PTPPort

ptp_port = PTPPort(
    domain_id=1,
    src_port_identity=1,
    sync_config=None,
)

print("SUCCESS")
sys.exit(0)
