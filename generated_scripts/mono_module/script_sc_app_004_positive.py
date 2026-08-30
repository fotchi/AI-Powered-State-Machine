import sys
from flync.model.flync_4_app.application import ServiceConsumerReference

service_consumer_reference = ServiceConsumerReference(
    type='consumer',
    service_id=123,
    instance_id=456,
    major_version=1
)

print("SUCCESS")
sys.exit(0)