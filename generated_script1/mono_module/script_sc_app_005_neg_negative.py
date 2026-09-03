import sys
from flync.model.flync_4_app.application import ServiceProviderReference
from pydantic import ValidationError

try:
    sp_ref = ServiceProviderReference(
        type='provider',
        service_id=123,
        instance_id=456,
        major_version=1,
        fields=['current_speed', 'rpm', 'unknown_field']
    )
except ValidationError as e:
    print("SUCCESS")
    sys.exit(0)
else:
    print("FAILURE")
    sys.exit(1)