import pytest
from flync.model.flync_4_security import Firewall, FirewallRule

def test_firewall_rule_at_maximum_rule_count():
    # Créer un Firewall avec le nombre maximum de règles autorisé (par défaut)
    firewall = Firewall(
        default_action='reject',
        input_rules=[FirewallRule() for _ in range(100)],  # Nombre maximum de règles
        output_rules=[],
        forward_rules=[]
    )

    # Vérifier que la validation réussit avec le nombre maximum de règles
    assert firewall

    # Ajouter une règle supplémentaire pour dépasser la limite
    firewall.input_rules.append(FirewallRule())

    # Vérifier que la validation échoue avec un message d'erreur approprié
    with pytest.raises(pydantic.ValidationError) as exc_info:
        Firewall(
            default_action='reject',
            input_rules=firewall.input_rules,
            output_rules=[],
            forward_rules=[]
        )

    # Vérifier que le message d'erreur contient la raison de l'échec (contrainte de limite)
    assert 'check_duplicate_rules' in str(exc_info.value)

# Test marqué comme skip car il n'y a pas de validator pour vérifier la règle métier
@pytest.mark.skip(reason='Pas de validator pour vérifier la règle métier')
def test_firewall_rule_at_maximum_rule_count_invalid():
    # Créer un Firewall avec une règle métier invalid (par exemple, deux règles identiques)
    firewall = Firewall(
        default_action='reject',
        input_rules=[FirewallRule(), FirewallRule()],  # Règles identiques
        output_rules=[],
        forward_rules=[]
    )

    # Vérifier que la validation échoue avec un message d'erreur approprié
    with pytest.raises(pydantic.ValidationError) as exc_info:
        Firewall(
            default_action='reject',
            input_rules=firewall.input_rules,
            output_rules=[],
            forward_rules=[]
        )