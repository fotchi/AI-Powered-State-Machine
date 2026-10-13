import sys

# OUT_OF_SCOPE: SC-SECURITY-003-NEG
# title: Invalid Firewall – Duplicate rule_id
# injected_fault: duplicate identifier (rule_id)
# Aucun validator Pydantic réel sur les classes résolues ne peut
# reproduire cette faute en isolation. Un test d'intégration
# au niveau FLYNCModel complet est requis.
print("OUT_OF_SCOPE: no validator can reproduce this fault in isolation")
sys.exit(1)
