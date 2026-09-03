"""
Scénario SC-SECURITY-001 (Negative)
MACsec channel without a matching key on the peer port

A MACsecConfig with IntegrityWithConfidentiality is applied to one port, but the connected peer port has no MACsec configuration.
"""
import pytest
# from flync.model.<module> import IntegrityWithConfidentiality  # TODO: ajuster le chemin exact


@pytest.mark.skip(reason="GAP DÉTECTÉ : IntegrityWithConfidentiality n'a aucun validator connu — impossible de tester 'asymmetric macsec configuration across a link' honnêtement. À clarifier avec KPIT avant de coder ce test.")
def test_sc_security_001():
    pass
