import sys
from pydantic import ValidationError

from flync.model.flync_4_someip.service_interface import SOMEIPMethod
from flync.model.flync_4_someip.service_interface import SOMEIPParameter

try:
    someip_method = SOMEIPMethod(
        name="demo_name",
        type='request_response',
        id=1,
    )
    someip_parameter = SOMEIPParameter(
        name="demo_name",
        description=None,
        datatype=None,
    )
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
except Exception as exc:
    print(f"UNEXPECTED ERROR: {type(exc).__name__}: {exc}")
    sys.exit(1)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)
