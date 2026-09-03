import sys
from flync.model.flync_4_app.application import ServiceConsumerReference

# Create a valid ServiceConsumerReference
consumer_reference = ServiceConsumerReference(
    service_name='DiagService',
    instance_id=1,
    major_version=1
)

print("SUCCESS")
sys.exit(0)