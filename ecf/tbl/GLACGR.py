from elixir import *
import sqlalchemy as sa
import re
import tools

class GLACGR(Entity):
  GLAGCONO    = Field(String(3), primary_key=True)
  GLAGACID    = Field(String(48), primary_key=True)
  GLAGACLV    = Field(Integer, index=True)
  GLAGACSQ    = Field(Integer, index=True)
  GLAGSTID    = Field(String(8))
  GLAGSTNM    = Field(String(32))
  GLAGACFM    = Field(String(48))
  GLAGACNM    = Field(String(32))
  GLAGACDS    = Field(String(48))
  GLAGACTP    = Field(String(1))
  GLAGGRTP    = Field(Integer, index=True)
  GLAGA1ID    = Field(String(48))
  GLAGA1FM    = Field(String(48))
  GLAGA1NM    = Field(String(32))
  GLAGA2ID    = Field(String(48))
  GLAGA2FM    = Field(String(48))
  GLAGA2NM    = Field(String(32))
  GLAGA3ID    = Field(String(48))
  GLAGA3FM    = Field(String(48))
  GLAGA3NM    = Field(String(32))
  GLAGA4ID    = Field(String(48))
  GLAGA4FM    = Field(String(48))
  GLAGA4NM    = Field(String(32))
  GLAGAUDT    = Field(Numeric(8,0))
  GLAGAUTM    = Field(Numeric(6,0))
  GLAGAUUS    = Field(String(24))





