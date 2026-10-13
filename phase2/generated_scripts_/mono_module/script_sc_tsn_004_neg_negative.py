import sys
from flync.model.flync_4_tsn.qos import CBSShaper
from pydantic import ValidationError

try:
    cbsshaper = CBSShaper(idleslope=10000000)
except ValidationError as e:
    sys.exit(0)

sys.exit(1)