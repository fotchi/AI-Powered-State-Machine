import pytest
from flync.model.flync_4_signal.frame import CANFrame

def test_valid_can_frame():
    can_frame = CANFrame(
        name="Test Frame",
        length=8,
        frame_usage=None,
        description=None,
        packed_pdus=[],
        can_id=0x123,
        id_format='standard_11bit',
        timing=None,
        type='can',
        is_remote_frame=False
    )

    assert can_frame.validate_can_frame_constraints() == True

def test_valid_can_frame_with_pdu():
    standard_pdu = {
        "pdu_type": "StandardPDU",
        "payload_size": 8,
        "data": b'\x00' * 8
    }

    can_frame = CANFrame(
        name="Test Frame",
        length=8,
        frame_usage=None,
        description=None,
        packed_pdus=[standard_pdu],
        can_id=0x123,
        id_format='standard_11bit',
        timing=None,
        type='can',
        is_remote_frame=False
    )

    assert can_frame.validate_can_frame_constraints() == True

def test_invalid_length():
    with pytest.raises(pydantic.ValidationError):
        CANFrame(
            name="Test Frame",
            length=9,  # Valeur en dehors des contraintes (0-8)
            frame_usage=None,
            description=None,
            packed_pdus=[],
            can_id=0x123,
            id_format='standard_11bit',
            timing=None,
            type='can',
            is_remote_frame=False
        )

def test_invalid_can_id():
    with pytest.raises(pydantic.ValidationError):
        CANFrame(
            name="Test Frame",
            length=8,
            frame_usage=None,
            description=None,
            packed_pdus=[],
            can_id=0x10000000,  # Valeur en dehors des contraintes (0-0x7FF)
            id_format='standard_11bit',
            timing=None,
            type='can',
            is_remote_frame=False
        )