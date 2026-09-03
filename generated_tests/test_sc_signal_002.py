"""
Scénario SC-SIGNAL-002 (Negative)
CAN Frame DLC smaller than referenced PDU

A CANFrame declares DLC=4 but its referenced StandardPDU has an 8-byte payload.
"""
import pytest
# from flync.model.<module> import CANFrame  # TODO: ajuster le chemin exact


def test_sc_signal_002():
    # Validators réels sur CANFrame: ['validate_can_frame_constraints']
    # TODO: modifier un des champs ci-dessous pour déclencher : size mismatch between frame and pdu
    with pytest.raises(Exception):
        canframe = CANFrame(
            name="demo_name",
            length=1,
            can_id=1,
            id_format='standard_11bit',
        )
