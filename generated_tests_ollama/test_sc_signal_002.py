import pydantic
import pytest
from agent_lecteur_out.flync_4_signal import CANFrame

def test_sc_signal_002():
    # Création d'un StandardPDU avec un payload de 8 octets
    standard_pdu = PDUInstance(payload=b'\x00' * 8)

    # Création d'un CANFrame avec DLC=4 mais référence à un StandardPDU avec un payload de 8 octets
    can_frame = CANFrame(
        name="Test Frame",
        length=4,
        packed_pdus=[standard_pdu],
        can_id=0x123,
        id_format="standard_11bit"
    )

    # Vérification que la construction du CANFrame échoue avec une erreur de taille
    with pytest.raises(pydantic.ValidationError):
        CANFrame.construct_from_pydantic(can_frame)