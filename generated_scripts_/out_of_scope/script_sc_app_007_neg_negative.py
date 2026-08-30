import sys

# OUT_OF_SCOPE: SC-APP-007-NEG
# title: Invalid AppBindings – Duplicate App Name
# injected_fault: duplicate identifier (App name appears twice in AppBindings)
# Aucun validator Pydantic réel sur les classes résolues ne peut
# reproduire cette faute en isolation. Un test d'intégration
# au niveau FLYNCModel complet est requis.
print("OUT_OF_SCOPE: no validator can reproduce this fault in isolation")
sys.exit(1)
