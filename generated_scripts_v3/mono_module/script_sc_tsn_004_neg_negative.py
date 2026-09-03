import sys
from pydantic import ValidationError
from flync.model.flync_4_tsn.qos import CBSShaper

try:
    cbsshaper = CBSShaper(idleslope=10000000)
except ValidationError as e:
    sys.exit(0)

sys.exit(1)