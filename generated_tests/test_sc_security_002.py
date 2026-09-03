"""
Scénario SC-SECURITY-002 (Boundary)
Firewall rule at maximum rule count

A Firewall config is populated with the maximum number of FirewallRule entries supported.
"""
import pytest
# from flync.model.<module> import Firewall  # TODO: ajuster le chemin exact


def test_sc_security_002_at_limit():
    firewall = Firewall(
    )
    # TODO: ajuster les champs ci-dessus à la valeur limite exacte du scénario
    assert firewall is not None


def test_sc_security_002_beyond_limit():
    with pytest.raises(Exception):
        Firewall(
            # TODO: mêmes champs que ci-dessus, en dépassant la limite
        )
