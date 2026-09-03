import sys
from flync.model.flync_4_app.application import ServiceConsumerReference
from pydantic import ValidationError

try:
    consumer = ServiceConsumerReference(
        type='consumer',
        service_id=123,
        instance_id=456,
        major_version=1,
        methods=['get_status', 'unknown_method']
    )
except ValidationError as e:
    sys.exit(0)

sys.exit(1)