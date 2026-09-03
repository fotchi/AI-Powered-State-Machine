import sys

# OUT_OF_SCOPE: SC-SIGNAL-003-NEG
# title: Text Table with Duplicate Raw Value
# injected_fault: duplicate identifier (IP, MAC, Service ID, Frame ID)
# Aucun validator Pydantic réel sur les classes résolues ne peut
# reproduire cette faute en isolation. Un test d'intégration
# au niveau FLYNCModel complet est requis.
print("OUT_OF_SCOPE: no validator can reproduce this fault in isolation")
sys.exit(1)
