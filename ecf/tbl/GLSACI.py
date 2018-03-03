from elixir import *

#
# Detail account structure
#

class GLSACI(Entity):
  AIASACCD  = Field(String(8), primary_key=True)
  AIASCSID  = Field(Integer,   primary_key=True)
  AIASCSNM  = Field(String(32))
  AIASCSIX  = Field(Integer, index=True)
  AIASAUDT  = Field(Numeric(8, 0))
  AIASAUTM  = Field(Numeric(6, 0))
  AIASAUUS  = Field(String(24))



