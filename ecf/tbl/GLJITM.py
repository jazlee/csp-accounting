from elixir import *
import sqlalchemy as sa
import datetime as dt

#
#   G/L Journal Entry Items
#

class GLJITM(Entity):
  GLJICONO  = Field(String(3), primary_key=True)
  GLJINOID  = Field(String(3), primary_key=True)
  GLJIBCID  = Field(Integer, primary_key=True)
  GLJIJEID  = Field(Integer, primary_key=True)
  GLJITRID  = Field(Integer, primary_key=True)
  GLJITRDT  = Field(Numeric(8,0))
  GLJITRDS  = Field(String(48))
  GLJITRRF  = Field(String(32))
  GLJISQNO  = Field(Integer)
  GLJIACID  = Field(String(48))
  GLJIACFM  = Field(String(48))
  GLJIACNM  = Field(String(32))
  GLJISRLG  = Field(String(2))
  GLJISRTP  = Field(String(2))
  GLJITRAM  = Field(Numeric(18,4))
  GLJITRDB  = Field(Numeric(18,4))
  GLJITRCR  = Field(Numeric(18,4))
  GLJITRTP  = Field(Integer)
  GLJICUDC  = Field(Integer)
  GLJICHCD  = Field(String(3))
  GLJICRTP  = Field(String(3))
  GLJIDTMT  = Field(String(1))
  GLJIRTOP  = Field(String(1))
  GLJIRTDT  = Field(Numeric(8,0))
  GLJIRCVL  = Field(Numeric(15,4))
  GLJIRTVL  = Field(Numeric(15,4))
  GLJIRTSP  = Field(Numeric(15,4))
  GLJICSCD  = Field(String(3))
  GLJICUAM  = Field(Numeric(18,4))
  GLJICUDB  = Field(Numeric(18,4))
  GLJICUCR  = Field(Numeric(18,4))
  GLJIAUDT  = Field(Numeric(8, 0))
  GLJIAUTM  = Field(Numeric(6, 0))
  GLJIAUUS  = Field(String(24))

  def getObj(cls, opt, **kwargs):
    q = cls.query
    if kwargs.has_key('GLJICONO') and (kwargs['GLJICONO'] not in (None, '')):
      q = q.filter_by(GLJICONO = kwargs.pop('GLJICONO', None))
    if kwargs.has_key('GLJINOID') and (kwargs['GLJINOID'] not in (None, '')):
      q = q.filter_by(GLJINOID = kwargs.pop('GLJINOID', None))
    if kwargs.has_key('GLJIBCID') and (kwargs['GLJIBCID'] not in (None, 0)):
      q = q.filter_by(GLJIBCID = kwargs.pop('GLJIBCID', None))
    if kwargs.has_key('GLJIJEID') and (kwargs['GLJIJEID'] not in (None, 0)):
      q = q.filter_by(GLJIJEID = kwargs.pop('GLJIJEID', None))
    if kwargs.has_key('GLJITRID') and (kwargs['GLJITRID'] not in (None, 0)):
      q = q.filter_by(GLJITRID = kwargs.pop('GLJITRID', None))
    q = q.order_by(sa.asc(GLJITM.GLJICONO))
    q = q.order_by(sa.asc(GLJITM.GLJINOID))
    q = q.order_by(sa.asc(GLJITM.GLJIBCID))
    q = q.order_by(sa.asc(GLJITM.GLJIJEID))
    q = q.order_by(sa.asc(GLJITM.GLJISQNO))
    if opt:
      obj = q.all()
    else:
      obj = q.first()
    return obj

  getObj = classmethod(getObj)

  def getTRNO(cls, obj):
    # obj is object of GLJHDR
    if not obj:
      raise Exception('Header transaction does not exist')
    ret = obj.GLJHLSTR + 1
    obj.GLJHLSTR = ret
    session.update(obj)
    return (ret, obj)

  getTRNO = classmethod(getTRNO)

  def delItems(cls, hdr, sesn):
    if hdr:
      itms = cls.getObj(True, GLJICONO = hdr.GLJHCONO, GLJINOID = hdr.GLJHNOID, \
              GLJIBCID = hdr.GLJHBCID, GLJIJEID = hdr.GLJHJEID)
      for itm in itms:
        sesn.delete(itm)

  delItems = classmethod(delItems)

