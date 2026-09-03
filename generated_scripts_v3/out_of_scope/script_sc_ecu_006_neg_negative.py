import sys

# OUT_OF_SCOPE: SC-ECU-006-NEG
# title: Multiple LIN Masters on Same Bus
# injected_fault: duplicate identifier (multiple LIN masters on a single bus)
# Aucun validator Pydantic réel sur les classes résolues ne peut
# reproduire cette faute en isolation. Un test d'intégration
# au niveau FLYNCModel complet est requis.
print("OUT_OF_SCOPE: no validator can reproduce this fault in isolation")
sys.exit(1)
