import sys

# OUT_OF_SCOPE: SC-APP-005-NEG
# title: Invalid ServiceProviderReference – Undefined Field
# injected_fault: missing or dangling reference (field not declared on provider side)
# Aucun validator Pydantic réel sur les classes résolues ne peut
# reproduire cette faute en isolation. Un test d'intégration
# au niveau FLYNCModel complet est requis.
print("OUT_OF_SCOPE: no validator can reproduce this fault in isolation")
sys.exit(1)
