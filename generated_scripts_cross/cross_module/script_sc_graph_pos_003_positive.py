import sys
from flync.model.flync_4_signal.pdu import StandardPDU
from flync.model.flync_4_communication.flync_channels import FLYNCChannelConfig

# Create a valid StandardPDU instance
standard_pdu = StandardPDU(
    name="ExamplePDU",
    length=10,
    pdu_usage="application",
    signals=[],
    signal_groups=[]
)

# Create a valid FLYNCChannelConfig instance with a reference to the StandardPDU
flync_channel_config = FLYNCChannelConfig(
    pdus=[standard_pdu]
)

# Print success message
print("SUCCESS")
sys.exit(0)