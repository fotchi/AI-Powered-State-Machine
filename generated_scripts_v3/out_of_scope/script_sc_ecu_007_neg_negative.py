import sys

# OUT_OF_SCOPE: SC-ECU-007-NEG
# title: Virtual Switch Missing Port Definitions
# injected_fault: missing or dangling reference (virtual switch without required ports)
# Aucun validator Pydantic réel sur les classes résolues ne peut
# reproduire cette faute en isolation. Un test d'intégration
# au niveau FLYNCModel complet est requis.
print("OUT_OF_SCOPE: no validator can reproduce this fault in isolation")
sys.exit(1)
