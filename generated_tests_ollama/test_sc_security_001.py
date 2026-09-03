import pytest
from flync.model.flync_4_security.macsec import IntegrityWithConfidentiality

def test_sc_security_001():
    # Création d'un objet MACsecConfig avec IntegrityWithConfidentiality
    macsec_config = IntegrityWithConfidentiality(
        type='integrity_with_confidentiality',
        offset_preference=30  # Valeur arbitraire, mais dans la plage autorisée
    )

    # Création d'un objet peer port sans MACsec configuration
    peer_port = {}

    # Essai de créer un objet avec les deux configurations
    with pytest.raises(pydantic.ValidationError):
        IntegrityWithConfidentiality(
            type='integrity_with_confidentiality',
            offset_preference=30,
            peer_port=peer_port  # Peer port sans MACsec configuration
        )

# Raisonnement : L'exception est levée car la configuration MACsec n'est pas présente sur le port pair.