import sys
from pydantic import ValidationError
from flync import SOMEIPDatatype

class LargePayload(SOMEIPDatatype):
    size = 2000

try:
    obj = LargePayload()
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)