from elixir import *

#
# Master cluster item definition
#

class GLSCSI(Entity):
  CSSICSID  = Field(Integer,   primary_key=True)
  CSSICSCD  = Field(String(48), primary_key=True)
  CSSICSDS  = Field(String(48))
  CSSICUCD  = Field(String(48))
  CSSICUNM  = Field(String(32))
  CSSIAUDT  = Field(Numeric(8, 0))
  CSSIAUTM  = Field(Numeric(6, 0))
  CSSIAUUS  = Field(String(24))

