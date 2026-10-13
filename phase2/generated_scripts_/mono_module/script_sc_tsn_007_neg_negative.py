import sys
from flync.model.flync_4_tsn.qos import TrafficClass
from pydantic import ValidationError

try:
    traffic_class = TrafficClass(
        name="example_traffic_class",
        priority=4,
        selection_mechanisms="non_existent_shaper"
    )
except ValidationError as e:
    sys.exit(0)

sys.exit(1)