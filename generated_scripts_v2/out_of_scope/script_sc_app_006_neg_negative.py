import sys

# OUT_OF_SCOPE: SC-APP-006-NEG
# title: Invalid App – Duplicate Instance ID
# injected_fault: duplicate identifier (instance_id collision)
# Aucun validator Pydantic réel sur les classes résolues ne peut
# reproduire cette faute en isolation. Un test d'intégration
# au niveau FLYNCModel complet est requis.
print("OUT_OF_SCOPE: no validator can reproduce this fault in isolation")
sys.exit(1)
