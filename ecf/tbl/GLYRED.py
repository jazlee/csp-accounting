from elixir import *

class GLYRED(Entity):
  GLYRJBID    = Field(String(38), primary_key=True)
  GLYRDESC    = Field(String(48))
  GLYRCONO    = Field(String(3))
  GLYRFSTP    = Field(Integer)
  GLYRFSYR    = Field(Integer)
  GLYRAUDT    = Field(Numeric(8,0))
  GLYRAUTM    = Field(Numeric(6,0))
  GLYRAUUS    = Field(String(24))