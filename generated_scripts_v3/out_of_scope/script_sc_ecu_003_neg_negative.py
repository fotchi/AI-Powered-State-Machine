import sys

# OUT_OF_SCOPE: SC-ECU-003-NEG
# title: Controller Missing Interface Configuration
# injected_fault: missing or dangling reference (controller lacks required interface definition)
# Aucun validator Pydantic réel sur les classes résolues ne peut
# reproduire cette faute en isolation. Un test d'intégration
# au niveau FLYNCModel complet est requis.
print("OUT_OF_SCOPE: no validator can reproduce this fault in isolation")
sys.exit(1)
