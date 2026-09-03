import sys
from pydantic import ValidationError
from flync.model.flync_4_app.application import App

try:
    app1 = App(name="App1", instance_id=1001)
    app2 = App(name="App2", instance_id=1001)
except ValidationError as e:
    print("SUCCESS")
    sys.exit(0)
else:
    print("FAILURE")
    sys.exit(1)