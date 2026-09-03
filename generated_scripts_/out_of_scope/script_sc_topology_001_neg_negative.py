import sys

# OUT_OF_SCOPE: SC-TOPOLOGY-001-NEG
# title: Invalid Ethernet Topology – Duplicate ExternalConnection Identifier
# injected_fault: duplicate identifier (ExternalConnection) – two connections share the same source/target pair
# Aucun validator Pydantic réel sur les classes résolues ne peut
# reproduire cette faute en isolation. Un test d'intégration
# au niveau FLYNCModel complet est requis.
print("OUT_OF_SCOPE: no validator can reproduce this fault in isolation")
sys.exit(1)
