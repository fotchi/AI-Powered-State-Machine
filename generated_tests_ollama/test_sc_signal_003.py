import pydantic
import pytest
from agent_lecteur_out.flync_4_signal  import CANFDFrame

def test_canfd_frame_at_max_payload():
    # Création d'un CANFDFrame avec un payload maximum de 64 bytes
    canfd_frame = CANFDFrame(
        name="Test Frame",
        length=64,
        frame_usage=None,
        description=None,
        packed_pdus=[],
        can_id=0x123,
        id_format='standard_11bit',
        timing=None,
        type='can_fd',
        bit_rate_switch=True,
        error_state_indicator=False
    )

    # Vérification que la validation réussit à 64 bytes
    assert canfd_frame.validate()

    # Modification du payload pour dépasser la limite de 64 bytes
    canfd_frame.length = 65

    # Vérification que la validation échoue à 65 bytes
    with pytest.raises(pydantic.ValidationError):
        canfd_frame.validate()