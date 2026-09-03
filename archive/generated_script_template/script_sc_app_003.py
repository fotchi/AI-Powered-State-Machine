import sys

from flync.model.flync_4_app.application import ServiceConsumerReference

service_consumer_reference = ServiceConsumerReference(
    instance_id=1,
    major_version=1,
)

print("SUCCESS")
sys.exit(0)
