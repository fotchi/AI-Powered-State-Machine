import sys
from flync.model.flync_4_app.application import ServiceConsumerReference
from flync.model.flync_4_app.application import ServiceProviderReference

service_provider_reference = ServiceProviderReference(
    type='provider',
    service_name='example_service',
    instance_id=123,
    major_version=1
)

service_consumer_reference = ServiceConsumerReference(
    type='consumer',
    service_name='example_service',
    instance_id=service_provider_reference.instance_id,
    major_version=service_provider_reference.major_version
)

print("SUCCESS")
sys.exit(0)