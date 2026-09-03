import sys

# OUT_OF_SCOPE: SC-NM-004-NEG
# title: Invalid SleepTiming – Wait Longer Than Timeout
# injected_fault: Logical error: wait_before_sleep_ms (2000) is greater than timeout_ms (1500).
# Aucun validator Pydantic réel sur les classes résolues ne peut
# reproduire cette faute en isolation. Un test d'intégration
# au niveau FLYNCModel complet est requis.
print("OUT_OF_SCOPE: no validator can reproduce this fault in isolation")
sys.exit(1)
