import sys
from flync.model.flync_4_app.application import ServiceProviderReference

# Création d'un instance de ServiceProviderReference avec les champs requis
service_provider_reference = ServiceProviderReference(
    type='provider',
    service_id=12345,
    instance_id=1,
    major_version=1
)

# Affichage du succès
print("SUCCESS")
sys.exit(0)