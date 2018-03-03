from elixir import *

#
# Master account cluster definition
#

class GLSCST(Entity):
  CSCPCSID  = Field(Integer, primary_key=True)
  CSCPCSNM  = Field(String(32))
  CSCPCSLN  = Field(Integer)
  CSCPCSCL  = Field(Integer)
  CSCPAUDT  = Field(Numeric(8, 0))
  CSCPAUTM  = Field(Numeric(6, 0))
  CSCPAUUS  = Field(String(24))



