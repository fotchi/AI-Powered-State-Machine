import sys
from pydantic import BaseModel
from flync import tcp_profiles

class TCPOption(BaseModel):
    profile = tcp_profiles.high_performance

obj = TCPOption()
print("SUCCESS")
sys.exit(0)