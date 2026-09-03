import sys

# OUT_OF_SCOPE: SC-SOMEIP-004-NEG
# title: Invalid SOMEIPRequestResponseMethod with Undefined Parameter Type
# injected_fault: missing or dangling reference (parameter type UNKNOWN_TYPE is not defined)
# Aucun validator Pydantic réel sur les classes résolues ne peut
# reproduire cette faute en isolation. Un test d'intégration
# au niveau FLYNCModel complet est requis.
print("OUT_OF_SCOPE: no validator can reproduce this fault in isolation")
sys.exit(1)
