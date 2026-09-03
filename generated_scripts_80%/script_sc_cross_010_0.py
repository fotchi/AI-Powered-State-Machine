import sys
from flync.model.flync_4_bus.can_bus import CANBus
from flync.model.flync_4_communication.flync_channels import FLYNCChannelConfig
from flync.model.flync_4_communication.flync_communication import FLYNCCommunicationConfig

can_frame = CANFrame(id=1, data=[1, 2, 3])
can_bus = CANBus(name="CAN Bus", baud_rate=1000000)
can_bus.frames.append(can_frame)

pdu_ref = "my_pdu"
pdu = StandardPDU(type="StandardPDU", name=pdu_ref, description="")
pdu_ref_obj = PDURef(ref=pdu_ref)

channel_config = FLYNCChannelConfig()
channel_config.can_buses.append(can_bus)
channel_config.pdus.append(pdu)

communication_config = FLYNCCommunicationConfig()
communication_config.channels = channel_config

print("SUCCESS")
sys.exit(0)