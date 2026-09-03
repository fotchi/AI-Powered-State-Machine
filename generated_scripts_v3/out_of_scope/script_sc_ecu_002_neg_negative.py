import sys

# OUT_OF_SCOPE: SC-ECU-002-NEG
# title: External PHY Port Missing MII Configuration
# injected_fault: missing or dangling reference (required mii_config not provided for external PHY)
# Aucun validator Pydantic réel sur les classes résolues ne peut
# reproduire cette faute en isolation. Un test d'intégration
# au niveau FLYNCModel complet est requis.
print("OUT_OF_SCOPE: no validator can reproduce this fault in isolation")
sys.exit(1)
