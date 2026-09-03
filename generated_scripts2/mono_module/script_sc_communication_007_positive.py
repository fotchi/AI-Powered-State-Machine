import sys
from flync.model.flync_4_communication.flync_channels import FLYNCChannelConfig, StandardPDU

# Create a valid PDU definition
pdu = StandardPDU(
    name="EngineSpeed",
    signals=[],
    length=2
)

# Create a FLYNCChannelConfig with the valid PDU
channel_config = FLYNCChannelConfig(pdus=[pdu])

# Print success message
print("SUCCESS")
sys.exit(0)