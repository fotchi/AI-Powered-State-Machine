import sys
from flync.model.flync_4_communication.flync_channels import FLYNCChannelConfig
from flync.model.flync_4_signal.pdu import StandardPDU
pdu = StandardPDU(name="MyPDU", length=8)
config = FLYNCChannelConfig(pdus=[pdu])
print("SUCCESS")
sys.exit(0)