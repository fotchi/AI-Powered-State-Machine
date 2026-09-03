import sys
from flync.model.flync_4_someip.service_interface import SOMEIPMethod, SOMEIPParameter

try:
    param = SOMEIPParameter(name="param1", description="A parameter", datatype="FooBar")
    method = SOMEIPMethod(name="method1", description="A method", type="request_response", id=0x02, input_parameters=[param])
except Exception as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)