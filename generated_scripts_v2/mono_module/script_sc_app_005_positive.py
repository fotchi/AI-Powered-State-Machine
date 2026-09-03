import sys
from flync.model.flync_4_app.application import ServiceProviderReference

# Création d'un objet ServiceProviderReference avec les champs obligatoires
service_provider_reference = ServiceProviderReference(
    type='provider',
    service_id=12345,
    instance_id=1,
    major_version=1
)

print("SUCCESS")
sys.exit(0)