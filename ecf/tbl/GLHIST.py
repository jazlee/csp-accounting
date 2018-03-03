from elixir import *
import sqlalchemy as sa
import datetime as dt

#
#   G/L History
#

class GLHIST(Entity):
  GLHICONO  = Field(String(3), primary_key=True)
  GLHIFSTP  = Field(Integer, primary_key=True)
  GLHIFSYR  = Field(Integer, primary_key=True)
  GLHIIDNO  = Field(Integer, primary_key=True)
  GLHIFSPR  = Field(Integer, index=True)
  GLHIJEDT  = Field(Numeric(8,0))
  GLHIJEDS  = Field(String(48))
  GLHIHSSR  = Field(String(2))
  GLHIHSTP  = Field(String(2))
  GLHITRDT  = Field(Numeric(8,0))
  GLHITRDS  = Field(String(48))
  GLHITRRF  = Field(String(32))
  GLHIACID  = Field(String(48))
  GLHIACFM  = Field(String(48))
  GLHIACNM  = Field(String(32))
  GLHISRLG  = Field(String(2))
  GLHISRTP  = Field(String(2))
  GLHITRAM  = Field(Numeric(18,4))
  GLHITRDB  = Field(Numeric(18,4))
  GLHITRCR  = Field(Numeric(18,4))
  GLHITRTP  = Field(Integer)
  GLHICUDC  = Field(Integer)
  GLHICHCD  = Field(String(3))
  GLHICRTP  = Field(String(3))
  GLHIDTMT  = Field(String(1))
  GLHIRTOP  = Field(String(1))
  GLHIRTDT  = Field(Numeric(8,0))
  GLHIRTVL  = Field(Numeric(15,4))
  GLHIRTSP  = Field(Numeric(15,4))
  GLHICSCD  = Field(String(3))
  GLHICUAM  = Field(Numeric(18,4))
  GLHICUDB  = Field(Numeric(18,4))
  GLHICUCR  = Field(Numeric(18,4))
  GLHINOID  = Field(String(3))
  GLHIBCID  = Field(Integer)
  GLHIJEID  = Field(Integer)
  GLHITRID  = Field(Integer)
  GLHIAUDT  = Field(Numeric(8, 0))
  GLHIAUTM  = Field(Numeric(6, 0))
  GLHIAUUS  = Field(String(24))

  def getLastIDNO(cls, cono, fstp, fsyr):
    q = cls.query
    q = q.filter_by(GLHICONO = cono)
    q = q.filter_by(GLHIFSTP = fstp)
    q = q.filter_by(GLHIFSYR = fsyr)
    q = q.order_by(sa.asc(GLHIST.GLHICONO))
    q = q.order_by(sa.asc(GLHIST.GLHIFSTP))
    q = q.order_by(sa.asc(GLHIST.GLHIFSYR))
    q = q.order_by(sa.desc(GLHIST.GLHIIDNO))
    obj = q.first()
    if not obj:
      return 1
    else:
      return obj.GLHIIDNO + 1

  getLastIDNO = classmethod(getLastIDNO)
