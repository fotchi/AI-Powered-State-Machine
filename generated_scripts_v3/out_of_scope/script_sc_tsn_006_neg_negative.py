import sys

# OUT_OF_SCOPE: SC-TSN-006-NEG
# title: Invalid Stream – Malformed Stream ID
# injected_fault: malformed identifier (non‑hex characters in streamId)
# Aucun validator Pydantic réel sur les classes résolues ne peut
# reproduire cette faute en isolation. Un test d'intégration
# au niveau FLYNCModel complet est requis.
print("OUT_OF_SCOPE: no validator can reproduce this fault in isolation")
sys.exit(1)
