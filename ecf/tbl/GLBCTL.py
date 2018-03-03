from elixir import *
import sqlalchemy as sa
import datetime as dt

#
# G/L Batch List
#

class GLBCTL(Entity):
  GLBCCONO  = Field(String(3), primary_key=True)
  GLBCNOID  = Field(String(3), primary_key=True)
  GLBCLSID  = Field(Integer, primary_key=True)
  GLBCNODS  = Field(String(32))
  GLBCLSTR  = Field(Integer)
  GLBCCTTR  = Field(Integer)
  GLBCCTER  = Field(Integer)
  GLBCNTDB  = Field(Numeric(18,4))
  GLBCNTCR  = Field(Numeric(18,4))
  GLBCPRST  = Field(Integer)
  GLBCDTCR  = Field(Numeric(8,0))
  GLBCDTED  = Field(Numeric(8,0))
  GLBCSRLG  = Field(String(2))
  GLBCBCTP  = Field(Integer)
  GLBCBCST  = Field(Integer, index=True)
  GLBCPSSQ  = Field(Integer)
  GLBCAUDT  = Field(Numeric(8, 0))
  GLBCAUTM  = Field(Numeric(6, 0))
  GLBCAUUS  = Field(String(24))

  def getObj(cls, opt, **kwargs):
    q = cls.query
    if kwargs.has_key('GLBCCONO') and (kwargs['GLBCCONO'] not in (None, '')):
      q = q.filter_by(GLBCCONO = kwargs.pop('GLBCCONO', None))
    if kwargs.has_key('GLBCNOID') and (kwargs['GLBCNOID'] not in (None, '')):
      q = q.filter_by(GLBCNOID = kwargs.pop('GLBCNOID', None))
    if kwargs.has_key('GLBCBCST') and (kwargs['GLBCBCST'] not in (None, 0)):
      q = q.filter_by(GLBCBCST = kwargs.pop('GLBCBCST', None))
    if kwargs.has_key('GLBCLSID') and (kwargs['GLBCLSID'] not in (None, 0)):
      q = q.filter_by(GLBCLSID = kwargs.pop('GLBCLSID', None))
    q = q.order_by(sa.asc(GLBCTL.GLBCCONO))
    q = q.order_by(sa.asc(GLBCTL.GLBCNOID))
    q = q.order_by(sa.desc(GLBCTL.GLBCLSID))
    if opt:
      obj = q.all()
    else:
      obj = q.first()
    return obj

  getObj = classmethod(getObj)

  def assignNewBatch(cls, cono, bcno, bcds, srclgr, usr_name):
    from tbl import GLBCNO
    bclsid = GLBCNO.getLSNO(bcno)
    obj = cls.getObj(False, GLBCCONO = cono, GLBCNOID = bcno, GLBCLSID = bclsid)
    td = dt.datetime.now()
    if not obj:
      obj = object.__new__(cls)
      obj.__init__(
          GLBCCONO  = cono,
          GLBCNOID  = bcno,
          GLBCLSID  = bclsid,
          GLBCNODS  = bcds,
          GLBCLSTR  = 0,
          GLBCCTTR  = 0,
          GLBCCTER  = 0,
          GLBCNTDB  = 0,
          GLBCNTCR  = 0,
          GLBCPRST  = 0,
          GLBCDTCR  = td.date().tointeger(),
          GLBCDTED  = td.date().tointeger(),
          GLBCSRLG  = srclgr,
          GLBCBCTP  = 1,
          GLBCBCST  = 1,
          GLBCPSSQ  = 0,
          GLBCAUDT  = td.date().tointeger(),
          GLBCAUTM  = td.time().tointeger(),
          GLBCAUUS  = usr_name
        )
      try:
        session.save(obj)
        session.commit()
      except:
        session.rollback()
        session.expunge(obj)
        raise
    return (bclsid, obj)

  assignNewBatch = classmethod(assignNewBatch)

  def getLSNO(cls, cono, bcno, bclsid):
    if bcno in (None, ''):
      raise Exception('Default batch option has not been setup properly')
    q = cls.query
    q = q.filter_by(GLBCCONO = cono)
    q = q.filter_by(GLBCNOID = bcno)
    q = q.filter_by(GLBCLSID = bclsid)
    obj = q.first()
    if not obj:
      raise Exception('Batch number %.6d does not exist' % bclsid)

    ret = obj.GLBCLSTR + 1
    try:
      obj.GLBCLSTR = ret
      session.update(obj)
      session.commit()
    except:
      session.expunge(obj)
      session.rollback()
    return ret

  getLSNO = classmethod(getLSNO)







