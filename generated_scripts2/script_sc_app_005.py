import sys
from flync.model.flync_4_app.application import ServiceProviderReference

provider_ref = ServiceProviderReference(
    instance_id=123,
    major_version=1
)

print("SUCCESS")
sys.exit(0)