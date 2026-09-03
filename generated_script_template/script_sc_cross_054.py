import sys
from pydantic import ValidationError

from flync.model.flync_4_tsn.qos import FrameFilter
from flync.model.flync_4_someip.service_interface import SDConfig
from flync.model.flync_4_someip.service_interface import SDTimings
from flync.model.flync_4_tsn.qos import SingleRateTwoColorMarker
from flync.model.flync_4_tsn.qos import Stream

try:
    frame_filter = FrameFilter(
    )
    sd_config = SDConfig(
        ip_address=None,
        sd_timings=[],
    )
    sd_timings = SDTimings(
        profile_id="demo_profile_id",
    )
    single_rate_two_color_marker = SingleRateTwoColorMarker(
        cir=1,
        cbs=1,
        eir=0,
        ebs=1,
        coupling=False,
    )
    stream = Stream(
        name="demo_name",
        stream_identification=[],
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
