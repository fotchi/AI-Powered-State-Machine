import sys
from pydantic import ValidationError
from flync import MultiplexedPDU, SelectorMapping

scenario = {
    "type": "Negative",
    "description": "Invalid MultiplexedPDU with Undefined Selector Value"
}

selector_mapping = SelectorMapping(
    selector_signals=[{"id": 1, "name": "Selector 1", "pdu_id": 10}],
    selector_signal_pdu_map={
        1: {"pdu_id": 10}
    }
)

multiplexed_pdu = MultiplexedPDU(
    pdu_id=10,
    selector_value=99
)

try:
    multiplexed_pdu = MultiplexedPDU(
        pdu_id=10,
        selector_value=99
    )
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)