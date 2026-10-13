import sys

# OUT_OF_SCOPE: SC-SOMEIP-003-NEG
# title: Invalid SOMEIPServiceInterface with Duplicate Service ID
# injected_fault: duplicate identifier (service_identifier already exists)
# Aucun validator Pydantic réel sur les classes résolues ne peut
# reproduire cette faute en isolation. Un test d'intégration
# au niveau FLYNCModel complet est requis.
print("OUT_OF_SCOPE: no validator can reproduce this fault in isolation")
sys.exit(1)
