import sys
from pydantic import BaseModel
from flync import RealFlyncClass

class RealFlyncClass(BaseModel):
    pid: int = 5

try:
    obj = RealFlyncClass()
    print("SUCCESS")
except Exception as exc:
    print(f"UNEXPECTED ERROR: {type(exc).__name__}: {exc}")
    sys.exit(1)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)

sys.exit(0)