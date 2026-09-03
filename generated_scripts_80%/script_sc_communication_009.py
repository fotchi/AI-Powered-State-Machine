import sys
from pydantic import BaseModel, IPvAnyAddress
from flync import UDPOption

class UDPOption(BaseModel):
    option_class = 0x0001
    option_number = 0x0014
    data = IPvAnyAddress("2001:db8::1")

obj = UDPOption()
print("SUCCESS")
sys.exit(0)