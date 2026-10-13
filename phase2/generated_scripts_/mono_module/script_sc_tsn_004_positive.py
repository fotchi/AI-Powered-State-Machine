import sys
from flync.model.flync_4_tsn.qos import CBSShaper

cbsshaper = CBSShaper(idleslope=500000)
print("SUCCESS")
sys.exit(0)