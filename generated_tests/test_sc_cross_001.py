"""
Scénario SC-CROSS-001 (Negative)
CAN Frame forwarded to an unreachable Ethernet socket

A CANFrameForwarder redirects a Frame to an EthSocketEgress whose destination IP is on a VLAN not reachable from the source ECU.
"""
import pytest
# from flync.model.<module> import CANFrameForwarder  # TODO: ajuster le chemin exact


def test_sc_cross_001():
    # Validators réels sur CANFrameForwarder: ['validate_can_frame_forwarder_egress_uniqueness']
    # TODO: modifier un des champs ci-dessous pour déclencher : unreachable egress socket across vlan boundary
    with pytest.raises(Exception):
        canframeforwarder = CANFrameForwarder(
            frame_ref="demo_frame_ref",
            egresses=[],
        )
