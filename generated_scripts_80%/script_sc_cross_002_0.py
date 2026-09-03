import sys
from flync.model.flync_4_ecu.controller import Controller
from flync.model.flync_4_app.app_bindings import AppBindings
from flync.model.flync_4_app.application import ServiceProviderReference
from pydantic import BaseModel, Field, EmbeddedMetadata

class EmbeddedMetadata(BaseModel):
    pass

scenario = {
    'type': 'Positive',
    'description': 'Valid App Binding of ServiceProvider to ECU Controller'
}

app_bindings = AppBindings(
    app_refs=['flync_4_app.app1', 'flync_4_app.app2']
)

controller_metadata = EmbeddedMetadata()

controller = Controller(
    name='hpc_controller1',
    controller_metadata=controller_metadata,
    ethernet_interfaces=[],
    can_interfaces=[],
    lin_interfaces=[],
    virtual_switch=None,
    app_bindings=app_bindings,
    state_memberships=[]
)

service_provider_reference = ServiceProviderReference(
    type='provider',
    service_name='consumer',
    instance_id=12345,
    major_version=1
)

print("SUCCESS")
sys.exit(0)