from elixir import *
import sqlalchemy as sa
import datetime as dt

#
#   G/L Journal Entry Header
#

class GLJHDR(Entity):
  GLJHCONO  = Field(String(3), primary_key=True)
  GLJHNOID  = Field(String(3), primary_key=True)
  GLJHBCID  = Field(Integer, primary_key=True)
  GLJHJEID  = Field(Integer, primary_key=True)
  GLJHBCDS  = Field(String(32))
  GLJHFSYR  = Field(Integer)
  GLJHFSPR  = Field(Integer)
  GLJHJEDS  = Field(String(48))
  GLJHJEDT  = Field(Numeric(8,0))
  GLJHDTCR  = Field(Numeric(8,0))
  GLJHDTED  = Field(Numeric(8,0))
  GLJHSRLG  = Field(String(2))
  GLJHSRTP  = Field(String(2))
  GLJHJERV  = Field(Integer)
  GLJHJEST  = Field(Integer)
  GLJHJEED  = Field(Integer)
  GLJHLSTR  = Field(Integer)
  GLJHNTDB  = Field(Numeric(18,4))
  GLJHNTCR  = Field(Numeric(18,4))
  GLJHAUDT  = Field(Numeric(8, 0))
  GLJHAUTM  = Field(Numeric(6, 0))
  GLJHAUUS  = Field(String(24))

  def getObj(cls, opt, **kwargs):
    q = cls.query
    if kwargs.has_key('GLJHCONO') and (kwargs['GLJHCONO'] not in (None, '')):
      q = q.filter_by(GLJHCONO = kwargs.pop('GLJHCONO', None))
    if kwargs.has_key('GLJHNOID') and (kwargs['GLJHNOID'] not in (None, '')):
      q = q.filter_by(GLJHNOID = kwargs.pop('GLJHNOID', None))
    if kwargs.has_key('GLJHBCID') and (kwargs['GLJHBCID'] not in (None, 0)):
      q = q.filter_by(GLJHBCID = kwargs.pop('GLJHBCID', None))
    if kwargs.has_key('GLJHJEID') and (kwargs['GLJHJEID'] not in (None, 0)):
      q = q.filter_by(GLJHJEID = kwargs.pop('GLJHJEID', None))
    q = q.order_by(sa.asc(GLJHDR.GLJHCONO))
    q = q.order_by(sa.asc(GLJHDR.GLJHNOID))
    q = q.order_by(sa.asc(GLJHDR.GLJHBCID))
    q = q.order_by(sa.desc(GLJHDR.GLJHJEID))
    if opt:
      return q.all()
    else:
      return q.first()

  getObj = classmethod(getObj)

  def getLSNO(cls, obj):
    # obj is object of GLBCTL
    if not obj:
      raise Exception('Batch number does not exist')
    ret = obj.GLBCLSTR + 1
    obj.GLBCLSTR = ret
    obj.GLBCCTTR = obj.GLBCCTTR + 1
    session.update(obj)
    return (ret, obj)

  getLSNO = classmethod(getLSNO)

  def delItems(cls, hdr, sesn):
    from tbl import GLJITM
    if hdr:
      hdrs = cls.getObj(True, GLJHCONO = hdr.GLBCCONO, GLJHNOID = hdr.GLBCNOID, \
              GLJHBCID = hdr.GLBCLSID)
      for hdr in hdrs:
        GLJITM.delItems(hdr, sesn)
        sesn.delete(hdr)

  delItems = classmethod(delItems)




