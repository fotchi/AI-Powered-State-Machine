import sys
from flync.model.flync_4_app.application import ServiceConsumerReference

# Création d'un objet ServiceConsumerReference avec les valeurs du scénario
service_consumer_reference = ServiceConsumerReference(
    type='consumer',
    service_id=12345,
    instance_id=0,
    major_version=1
)

# Affichage du succès
print("SUCCESS")
sys.exit(0)