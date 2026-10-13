import sys

# OUT_OF_SCOPE: SC-METADATA-001-NEG
# title: Invalid SystemMetadata – Duplicate System Name
# injected_fault: duplicate identifier (system name)
# Aucun validator Pydantic réel sur les classes résolues ne peut
# reproduire cette faute en isolation. Un test d'intégration
# au niveau FLYNCModel complet est requis.
print("OUT_OF_SCOPE: no validator can reproduce this fault in isolation")
sys.exit(1)
