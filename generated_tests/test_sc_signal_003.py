"""
Scénario SC-SIGNAL-003 (Boundary)
CAN FD Frame at maximum 64-byte payload

A CANFDFrame is configured with the maximum allowed payload of 64 bytes.
"""
import pytest
# from flync.model.<module> import CANFDFrame  # TODO: ajuster le chemin exact


def test_sc_signal_003_at_limit():
    canfdframe = CANFDFrame(
        name="demo_name",
        length=1,
        can_id=1,
        id_format='standard_11bit',
    )
    # TODO: ajuster les champs ci-dessus à la valeur limite exacte du scénario
    assert canfdframe is not None


def test_sc_signal_003_beyond_limit():
    with pytest.raises(Exception):
        CANFDFrame(
            # TODO: mêmes champs que ci-dessus, en dépassant la limite
        )
