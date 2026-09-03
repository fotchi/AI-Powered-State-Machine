import sys

# OUT_OF_SCOPE: SC-SOMEIP-001-NEG
# title: Invalid SOMEIPConfig with Non‑existent Directory Path
# injected_fault: missing or dangling reference (configuration directory does not exist)
# Aucun validator Pydantic réel sur les classes résolues ne peut
# reproduire cette faute en isolation. Un test d'intégration
# au niveau FLYNCModel complet est requis.
print("OUT_OF_SCOPE: no validator can reproduce this fault in isolation")
sys.exit(1)
