import sys
from flync.model.flync_4_app.application import ServiceConsumerReference

app = ServiceConsumerReference(
    type='consumer',
    service_id=12345,
    instance_id=1,
    major_version=1
)

print("SUCCESS")
sys.exit(0)