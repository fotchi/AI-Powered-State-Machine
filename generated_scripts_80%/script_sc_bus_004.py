import sys
from pydantic import ValidationError
from flync import LinBusDefinition, LinScheduleTableEntry

scenario = {
    "type": "Negative",
    "description": "Missing Frame Reference in LIN Schedule Table"
}

bus_definition = LinBusDefinition(
    name="Test Bus",
    frames=["Frame1", "Frame2"],
)

schedule_table_entry = LinScheduleTableEntry(
    frame_name="InvalidFrame",
    schedule=[],
)

try:
    bus_definition.validate()
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)