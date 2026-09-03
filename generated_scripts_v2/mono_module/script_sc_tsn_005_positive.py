import sys
from flync.model.flync_4_tsn.qos import HTBInstance

htb_instance = HTBInstance(
    root_id="0:",
    default_class=None,
    child_classes=[]
)

print("SUCCESS")
sys.exit(0)