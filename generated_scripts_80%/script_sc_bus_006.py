import sys
from pydantic import ValidationError
from flync import LinScheduleTableEntry, LinBusDefinition

scenario = {
    "type": "Negative",
    "description": "LIN Schedule Table Timing Conflict"
}

lin_schedule_table_entry = LinScheduleTableEntry(
    start_time=1000,
    end_time=500,
    schedule_id="SCHEDULE_ID_1",
    bus_cycle_length=200
)

try:
    lin_bus_definition = LinBusDefinition(
        name="LIN_BUS_DEFINITION_1",
        baud_rate=1000000,
        data_bits=8,
        stop_bits=1,
        parity=None,
        lin_schedule_table=[lin_schedule_table_entry]
    )
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)