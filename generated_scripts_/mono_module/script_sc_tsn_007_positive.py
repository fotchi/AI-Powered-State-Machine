import sys
from flync.model.flync_4_tsn.qos import CBSShaper
from flync.model.flync_4_tsn.qos import TrafficClass

cbsshaper = CBSShaper(type='cbs', idleslope=1000)
trafficclass = TrafficClass(name='class3', priority=3, frame_priority_values=[3], selection_mechanisms=cbsshaper)

print("SUCCESS")
sys.exit(0)