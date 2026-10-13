import sys

# OUT_OF_SCOPE: SC-NM-001-NEG
# title: Invalid StateManagementGroup – Missing Timing Profile
# injected_fault: Dangling reference: timing_profile 'nonexistent_profile' does not exist in timing_profiles.flync.yaml.
# Aucun validator Pydantic réel sur les classes résolues ne peut
# reproduire cette faute en isolation. Un test d'intégration
# au niveau FLYNCModel complet est requis.
print("OUT_OF_SCOPE: no validator can reproduce this fault in isolation")
sys.exit(1)
