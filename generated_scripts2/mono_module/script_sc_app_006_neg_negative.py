import sys
from flync.model.flync_4_app.application import App
from pydantic import ValidationError

try:
    app = App(
        name="NewApp",
        instance_id=1001,
        service_consumer_refs=[],
        service_provider_refs=[]
    )
except ValidationError as e:
    sys.exit(0)

sys.exit(1)