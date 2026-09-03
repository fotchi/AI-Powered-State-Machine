"""
Scénario SC-SOMEIP-002 (Negative)
Subscribe to a non-existent Eventgroup

A SOMEIPServiceConsumer references an Eventgroup ID that is not declared on the provider's service interface.
"""
import pytest
# from flync.model.<module> import SOMEIPServiceConsumer  # TODO: ajuster le chemin exact


@pytest.mark.skip(reason="GAP DÉTECTÉ : SOMEIPServiceConsumer n'a aucun validator connu — impossible de tester 'dangling eventgroup reference' honnêtement. À clarifier avec KPIT avant de coder ce test.")
def test_sc_someip_002():
    pass
