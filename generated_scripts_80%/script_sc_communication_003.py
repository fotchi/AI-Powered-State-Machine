import sys
from pydantic import BaseModel
from flync import UDPOption

class UDPOption(BaseModel):
    port: int
    option_name: str

udp_option = UDPOption(port=5000, option_name="example")
print("SUCCESS")
sys.exit(0)