import sys

from flync.model.flync_4_ecu.sockets import DeploymentUnion
from flync.model.flync_4_signal.forwarder import PDUForwarder

deployment_union = DeploymentUnion(
    root=None,
)
pdu_forwarder = PDUForwarder(
    pdu_ref="demo_pdu_ref",
    egresses=[],
)

print("SUCCESS")
sys.exit(0)
