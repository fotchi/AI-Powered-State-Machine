import sys
from flync.model.flync_4_someip.service_interface import SOMEIPEvent, SOMEIPEventgroup

# Création des événements
event1 = SOMEIPEvent(name="Event1", id=0x10)
event2 = SOMEIPEvent(name="Event2", id=0x11)

# Création du groupe d'événements
eventgroup = SOMEIPEventgroup(name="EventGroup1", id=0x01, events=[event1, event2])

print("SUCCESS")
sys.exit(0)