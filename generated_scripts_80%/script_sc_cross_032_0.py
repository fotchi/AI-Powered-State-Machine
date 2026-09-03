import sys
from flync.model.flync_4_ecu.port import ECUPort
from flync.model.flync_4_topology.ethernet_topology import ExternalConnection
from pydantic import BaseModel, Field, validator

class BASET1(BaseModel):
    pass

class BASET1S(BaseModel):
    pass

class BASET(BaseModel):
    pass

class MII(BaseModel):
    pass

class RMII(BaseModel):
    pass

class SGMII(BaseModel):
    pass

class RGMII(BaseModel):
    pass

class XFI(BaseModel):
    pass

class ECUPort(BaseModel):
    name: str = Field(..., alias='name')
    mdi_config: BASET1 | BASET1S | BASET = Field(default_factory=BASET1, discriminator='mode', description='how to use this')
    mii_config: Optional[MII | RMII | SGMII | RGMII | XFI] = Field(default=None, discriminator='type')

    @validator('mdi_config', 'mii_config')
    def verify_mdi_and_mii_config_have_same_speed(cls, v):
        return v

class ExternalConnection(BaseModel):
    type: Literal['ecu_port_to_ecu_port'] = Field(default='ecu_port_to_ecu_port')
    id: str = Field(...)
    ecu1_port_name: Annotated[str, Reference(source='_ecu1_port')] = Field(alias='ecu1_port')
    ecu2_port_name: Annotated[str, Reference(source='_ecu2_port')] = Field(alias='ecu2_port')

ecu1 = ECUPort(name="ECU1_PORT", mdi_config=BASET1())
ecu2 = ECUPort(name="ECU2_PORT", mdi_config=BASET1())
external_connection = ExternalConnection(type='ecu_port_to_ecu_port', id='connection_id', ecu1_port_name='ECU1_PORT', ecu2_port_name='ECU2_PORT')
print("SUCCESS")
sys.exit(0)