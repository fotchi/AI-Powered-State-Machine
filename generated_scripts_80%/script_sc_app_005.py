import sys
from flync.model.flync_4_app.application import ServiceProviderReference

sp_reference = ServiceProviderReference(
    type='provider',
    service_name='SOME/IP',
    instance_id=123,
    major_version=1
)

print("SUCCESS")
sys.exit(0)