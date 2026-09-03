import sys
from pydantic import ValidationError
from flync.model.flync_4_app.application import ServiceConsumerReference

try:
    consumer_ref = ServiceConsumerReference(
        type='consumer',
        service_id=123,
        instance_id=456,
        major_version=1,
        methods=['get_status', 'unknown_method']
    )
except ValidationError as e:
    sys.exit(0)

sys.exit(1)