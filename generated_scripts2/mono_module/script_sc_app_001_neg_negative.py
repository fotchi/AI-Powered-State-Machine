import sys
from flync.model.flync_4_app.application import ServiceConsumerReference
from pydantic import ValidationError

try:
    service_consumer_reference = ServiceConsumerReference(
        service_id=1,
        instance_id=1,
        major_version=1
    )
except ValidationError as e:
    print("Validation failed:", e)
    sys.exit(1)

print("SUCCESS")
sys.exit(0)