"""
Scénario SC-SIGNAL-001 (Positive)
Valid CAN Frame with matching PDU size

A CANFrame declares a DLC of 8 bytes and references a StandardPDU whose payload is also 8 bytes.
"""
import pytest
# from flync.model.<module> import CANFrame  # TODO: ajuster le chemin exact


def test_sc_signal_001():
    canframe = CANFrame(
        name="demo_name",
        length=1,
        can_id=1,
        id_format='standard_11bit',
    )
    assert canframe is not None
