import sys
from flync.model.flync_4_tsn.qos import CBSShaper

shaper = CBSShaper(idleSlope=5000, maxCredit=10000)
print("SUCCESS")
sys.exit(0)