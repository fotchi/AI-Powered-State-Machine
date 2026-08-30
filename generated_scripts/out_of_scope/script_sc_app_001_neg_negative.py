import sys

# OUT_OF_SCOPE: SC-APP-001-NEG
# title: Invalid ServiceConsumerReference – Dangling Service Identifier
# injected_fault: missing or dangling reference (ServiceConsumerReference points to undefined service)
# Aucun validator Pydantic réel sur les classes résolues ne peut
# reproduire cette faute en isolation. Un test d'intégration
# au niveau FLYNCModel complet est requis.
print("OUT_OF_SCOPE: no validator can reproduce this fault in isolation")
sys.exit(1)
