import sys
from flync.model.flync_4_app.application import ServiceConsumerReference

# Création d'un ServiceConsumerReference valide
service_consumer_reference = ServiceConsumerReference(
    service_id=123,
    instance_id=456,
    major_version=1
)

print("SUCCESS")
sys.exit(0)