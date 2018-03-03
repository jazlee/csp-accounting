from elixir import *

class GLBCRV(Entity):
  """
  This model purposed to hold initial request that required by
  G/L Revaluation Batch job process.
  """

  GLRVJBID    = Field(String(38), primary_key=True)
  GLRVDESC    = Field(String(48))
  GLRVCONO    = Field(String(3))
  GLRVCRBC    = Field(Integer)
  GLRVBCID    = Field(Integer)
  GLRVCUCD    = Field(String(3))
  GLRVACTP    = Field(Integer)
  GLRVACAL    = Field(Integer)
  GLRVACFR    = Field(String(48))
  GLRVACTO    = Field(String(48))
  GLRVRVNM    = Field(String(6))
  GLRVFSTP    = Field(Integer)
  GLRVFSYR    = Field(Integer)
  GLRVFPFR    = Field(Integer)
  GLRVFPTO    = Field(Integer)
  GLRVJEDT    = Field(Numeric(8,0))
  GLRVRTVL    = Field(Numeric(15, 4))
  GLRVRTDT    = Field(Numeric(8,0))
  GLRVFCRV    = Field(Integer)
  GLRVAUDT    = Field(Numeric(8,0))
  GLRVAUTM    = Field(Numeric(6,0))
  GLRVAUUS    = Field(String(24))
