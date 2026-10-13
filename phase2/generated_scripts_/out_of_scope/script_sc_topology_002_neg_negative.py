import sys

# OUT_OF_SCOPE: SC-TOPOLOGY-002-NEG
# title: Invalid ExternalConnection – Dangling Target Port Reference
# injected_fault: missing or dangling reference (target_port 'CAN_X' does not exist on ECU 'Sensor')
# Aucun validator Pydantic réel sur les classes résolues ne peut
# reproduire cette faute en isolation. Un test d'intégration
# au niveau FLYNCModel complet est requis.
print("OUT_OF_SCOPE: no validator can reproduce this fault in isolation")
sys.exit(1)
