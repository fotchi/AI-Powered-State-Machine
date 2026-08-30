import sys
from pydantic import ValidationError
from flync.model.flync_4_app.application import ServiceConsumerReference

try:
    service_consumer_reference = ServiceConsumerReference(
        type='consumer',
        service_id=123,
        instance_id=456,
        major_version=1,
        event_groups=['group_X']
    )
except ValidationError as e:
    sys.exit(0)

sys.exit(1)