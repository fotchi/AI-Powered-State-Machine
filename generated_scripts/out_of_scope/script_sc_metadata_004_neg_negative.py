import sys

# OUT_OF_SCOPE: SC-METADATA-004-NEG
# title: Invalid SoftwareBaseMetadata – Non‑PEP440 Version
# injected_fault: malformed version string (sw_version)
# Aucun validator Pydantic réel sur les classes résolues ne peut
# reproduire cette faute en isolation. Un test d'intégration
# au niveau FLYNCModel complet est requis.
print("OUT_OF_SCOPE: no validator can reproduce this fault in isolation")
sys.exit(1)
