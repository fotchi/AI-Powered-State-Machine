import sys
from flync.model.flync_4_app.application import ServiceConsumerReference
from flync.model.flync_4_app.application import ServiceProviderReference

app = ServiceConsumerReference(
    type='consumer',
    service_name='my_service',
    instance_id=123,
    major_version=1
)

provider_ref = ServiceProviderReference(
    type='provider',
    service_name='my_provider',
    instance_id=456,
    major_version=2
)

print("SUCCESS")
sys.exit(0)