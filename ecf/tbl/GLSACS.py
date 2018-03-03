from elixir import *

#
# Master account structure
#

class GLSACS(Entity):
  ACASACCD  = Field(String(8), primary_key=True)
  ACASACNM  = Field(String(32))
  ACASAUDT  = Field(Numeric(8, 0))
  ACASAUTM  = Field(Numeric(6, 0))
  ACASAUUS  = Field(String(24))



