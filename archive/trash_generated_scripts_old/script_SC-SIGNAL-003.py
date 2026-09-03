import sys
from flync_4_signal import CANFDFrame

def test_SC_Signal_003():
    # Crée un objet CANFDFrame avec le maximum de payload autorisé (64 bytes)
    canfd_frame = CANFDFrame(max_payload=64)

    # Vérifie si la création du CANFDFrame est réussie
    assert canfd_frame is not None

    # Tente de créer un CANFDFrame avec une taille de payload supérieure au maximum autorisé (65 bytes)
    with pytest.raises(ValueError):
        CANFDFrame(max_payload=65)

if __name__ == "__main__":
    test_SC_Signal_003()