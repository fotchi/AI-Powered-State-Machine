import sys

# OUT_OF_SCOPE: SC-SECURITY-005-NEG
# title: Invalid FirewallRule – Dangling destination reference
# injected_fault: missing or dangling reference (destination_address)
# Aucun validator Pydantic réel sur les classes résolues ne peut
# reproduire cette faute en isolation. Un test d'intégration
# au niveau FLYNCModel complet est requis.
print("OUT_OF_SCOPE: no validator can reproduce this fault in isolation")
sys.exit(1)
