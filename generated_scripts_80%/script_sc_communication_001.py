import sys
from pydantic import BaseModel
from flync.model.flync_4_communication.flync_channels import FLYNCChannelConfig, CANBus, LINBus, ContainerPDU, StandardPDU, MultiplexedPDU

scenario = {
    'type': 'Positive',
    'description': 'Valid FLYNCChannelConfig with Correct Bus and PDU Definitions'
}

class TestFLYNCChannelConfig(BaseModel):
    pdus: List[StandardPDU] = [
        StandardPDU(
            name='pdu1',
            description='Description of pdu1',
            type='uint8',
            size=2,
            offset=0
        ),
        StandardPDU(
            name='pdu2',
            description='Description of pdu2',
            type='uint16',
            size=4,
            offset=0
        )
    ]
    can_buses: List[CANBus] = [
        CANBus(
            id=0,
            bitrate=500000,
            name='can_bus1'
        ),
        CANBus(
            id=1,
            bitrate=1000000,
            name='can_bus2'
        )
    ]
    lin_buses: List[LINBus] = [
        LINBus(
            id=0,
            bitrate=1000000,
            name='lin_bus1'
        ),
        LINBus(
            id=1,
            bitrate=500000,
            name='lin_bus2'
        )
    ]
    ethernet_pdu_containers: List[ContainerPDU] = [
        ContainerPDU(
            name='container1',
            description='Description of container1',
            pdu_refs=['pdu1', 'pdu2']
        ),
        ContainerPDU(
            name='container2',
            description='Description of container2',
            pdu_refs=['pdu3', 'pdu4']
        )
    ]

try:
    flync_channel_config = FLYNCChannelConfig(
        pdus=TestFLYNCChannelConfig().pdus,
        can_buses=TestFLYNCChannelConfig().can_buses,
        lin_buses=TestFLYNCChannelConfig().lin_buses,
        ethernet_pdu_containers=TestFLYNCChannelConfig().ethernet_pdu_containers
    )
except Exception as e:
    print(f"UNEXPECTED ERROR: {type(e).__name__}: {e}")
    sys.exit(1)
else:
    print("SUCCESS")
    sys.exit(0)