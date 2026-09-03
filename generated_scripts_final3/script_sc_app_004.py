import sys
from pydantic import BaseModel, ValidationError
from pydantic import IPvAnyAddress
from pydantic import IPvAnyAddress

class Metadata(BaseModel):
    AppIdentifier: str = "App1"

class Interfaces(BaseModel):
    app_port: Ports.AppPort

class Ports(BaseModel):
    class AppPort(BaseModel):
        app_identifier: Metadata.AppIdentifier

try:
    metadata = Metadata(AppIdentifier="App1")
    interfaces = Interfaces(app_port=Ports.AppPort(app_identifier=metadata.AppIdentifier))
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)