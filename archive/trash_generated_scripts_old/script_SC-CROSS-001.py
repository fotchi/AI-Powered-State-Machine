import sys
from flync_4_signal import CANFrameForwarder
from flync_4_ecu import ECU
from flync_4_communication import EthSocketEgress, VLAN

def test_SC_CROSS_001():
    # Création d'un objet CANFrameForwarder
    forwarder = CANFrameForwarder()

    # Configuration de l'objet CANFrameForwarder
    forwarder.source_ecu = ECU()
    forwarder.destination_socket = EthSocketEgress()
    forwarder.destination_socket.vlan = VLAN()

    # Injection du défaut (unreachable egress socket across VLAN boundary)
    forwarder.destination_socket.vlan.id = 123  # ID de VLAN non atteignable

    try:
        # Tentative d'envoi du CANFrame
        forwarder.forward_frame()
    except Exception as e:
        print(f"Erreur : {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_SC_CROSS_001()