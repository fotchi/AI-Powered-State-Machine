import sys

from flync.model.flync_4_tsn.qos import CBSShaper

cbs_shaper = CBSShaper(
    idleslope=1,
)

print("SUCCESS")
sys.exit(0)
