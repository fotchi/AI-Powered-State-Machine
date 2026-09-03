import sys
from flync.model.flync_4_app.application import ServiceProviderReference

service_provider_reference = ServiceProviderReference(
    type='provider',
    service_id=123,
    instance_id=456,
    major_version=1
)

print("SUCCESS")
sys.exit(0)