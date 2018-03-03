from elixir import *

#
# G/L Options
#

class GLSOPT(Entity):
  GLOPCONO  = Field(String(3), primary_key=True)
  GLOPCLCD  = Field(String(48))
  GLOPPVST  = Field(Integer)
  GLOPPRST  = Field(Integer)
  GLOPFSTP  = Field(String(3))
  GLOPFSNM  = Field(String(24))
  GLOPFSYR  = Field(Integer)
  GLOPACSC  = Field(String(8))
  GLOPACSG  = Field(Integer)
  GLOPACDL  = Field(String(1))
  GLOPBCNO  = Field(String(3))
  GLOPAUDT  = Field(Numeric(8, 0))
  GLOPAUTM  = Field(Numeric(6, 0))
  GLOPAUUS  = Field(String(24))








