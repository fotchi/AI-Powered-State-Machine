import sys
from pydantic import ValidationError
from flync.model.flync_4_app.application import ServiceProviderReference

try:
    sp_ref = ServiceProviderReference(
        type='provider',
        service_id=123,
        instance_id=456,
        major_version=1,
        fields=['current_speed', 'rpm', 'unknown_field']
    )
except ValidationError as e:
    sys.exit(0)

sys.exit(1)