from elixir import *

acct_rule_list = {
      'INV_ACCT_ID':'Default Inventory Acct'
    }

class ACTRLS(Entity):
  ACRLCONO    = Field(String(3), primary_key=True)
  ACRLIDNO    = Field(String(32), primary_key=True)
  ACRLIDNM    = Field(String(48))
  ACRLACID    = Field(String(48))
  ACRLACFM    = Field(String(48))
  ACRLACNM    = Field(String(32))
  ACRLAUDT    = Field(Numeric(8,0))
  ACRLAUTM    = Field(Numeric(6,0))
  ACRLAUUS    = Field(String(24))

  def getObj(cls, opt, **kwargs):
    q = cls.query
    if kwargs.has_key('ACRLCONO') and (kwargs['ACRLCONO'] not in (None, '')):
      q = q.filter_by(ACRLCONO = kwargs.pop('ACRLCONO', None))
    if kwargs.has_key('ACRLIDNO') and (kwargs['ACRLIDNO'] not in (None, '')):
      q = q.filter_by(ACRLIDNO = kwargs.pop('ACRLIDNO', None))
    q = q.order_by(sa.asc(cls.ACRLCONO))
    q = q.order_by(sa.asc(cls.ACRLIDNO))
    if opt:
      return q.all()
    else:
      return q.first()

  getObj = classmethod(getObj)
