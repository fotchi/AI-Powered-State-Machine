import sys
from pydantic import ValidationError

class App:
    id: str
    name: str

try:
    app1 = App(id="my_app", name="My App")
    app2 = App(id="my_app", name="Another App")
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)