import sys

from flync.model.flync_4_tsn.qos import HTBInstance

htb_instance = HTBInstance(
    root_id="demo_root_id",
    child_classes=[],
)

print("SUCCESS")
sys.exit(0)
