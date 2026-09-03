import pydantic
import pytest
from agent_lecteur_out.flync_4_signal import CANFrameForwarder, ForwarderEgress

@pytest.fixture
def forwarder():
    return CANFrameForwarder(
        frame_ref="CAN_FRAME_ID",
        egresses=[
            ForwarderEgress(
                eth_socket_id="SOCKET_ID",
                destination_ip="192.168.1.100",  # IP sur une VLAN différente
                vlan_id=10,
            ),
        ],
    )

def test_SC_CROSS_001(forwarder):
    with pytest.raises(pydantic.ValidationError) as excinfo:
        CANFrameForwarder(
            frame_ref="CAN_FRAME_ID",
            egresses=[
                ForwarderEgress(
                    eth_socket_id="SOCKET_ID",
                    destination_ip="192.168.1.100",  # IP sur une VLAN différente
                    vlan_id=10,
                ),
            ],
        )
    assert "unreachable egress socket" in str(excinfo.value)
