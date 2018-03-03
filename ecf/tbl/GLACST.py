from elixir import *

class GLACST(Entity):
  """
  Account sets Module
  """
  GLACCONO    = Field(String(3), primary_key=True)
  GLACSTNM    = Field(String(6), primary_key=True)
  GLACSTDS    = Field(String(48))
  GLACACST    = Field(Integer)
  GLARCUCD    = Field(String(3))
  GLARCTAC    = Field(String(48))
  GLARCTFM    = Field(String(48))
  GLARCTNM    = Field(String(32))
  GLARDCAC    = Field(String(48))
  GLARDCFM    = Field(String(48))
  GLARDCNM    = Field(String(32))
  GLARPPAC    = Field(String(48))
  GLARPPFM    = Field(String(48))
  GLARPPNM    = Field(String(32))
  GLARWOAC    = Field(String(48))
  GLARWOFM    = Field(String(48))
  GLARWONM    = Field(String(32))
  GLARGXAC    = Field(String(48))
  GLARGXFM    = Field(String(48))
  GLARGXNM    = Field(String(32))
  GLARLXAC    = Field(String(48))
  GLARLXFM    = Field(String(48))
  GLARLXNM    = Field(String(32))
  GLARGRAC    = Field(String(48))
  GLARGRFM    = Field(String(48))
  GLARGRNM    = Field(String(32))
  GLARLRAC    = Field(String(48))
  GLARLRFM    = Field(String(48))
  GLARLRNM    = Field(String(32))
  GLAPCUCD    = Field(String(3))
  GLAPCTAC    = Field(String(48))
  GLAPCTFM    = Field(String(48))
  GLAPCTNM    = Field(String(32))
  GLAPDCAC    = Field(String(48))
  GLAPDCFM    = Field(String(48))
  GLAPDCNM    = Field(String(32))
  GLAPPPAC    = Field(String(48))
  GLAPPPFM    = Field(String(48))
  GLAPPPNM    = Field(String(32))
  GLAPGXAC    = Field(String(48))
  GLAPGXFM    = Field(String(48))
  GLAPGXNM    = Field(String(32))
  GLAPLXAC    = Field(String(48))
  GLAPLXFM    = Field(String(48))
  GLAPLXNM    = Field(String(32))
  GLAPGRAC    = Field(String(48))
  GLAPGRFM    = Field(String(48))
  GLAPGRNM    = Field(String(32))
  GLAPLRAC    = Field(String(48))
  GLAPLRFM    = Field(String(48))
  GLAPLRNM    = Field(String(32))
  GLACAUDT    = Field(Numeric(8,0))
  GLACAUTM    = Field(Numeric(6,0))
  GLACAUUS    = Field(String(24))

  def getObj(cls, opt, **kwargs):
    q = cls.query
    if kwargs.has_key('GLACCONO') and (kwargs['GLACCONO'] not in (None, '')):
      q = q.filter_by(GLACCONO = kwargs.pop('GLACCONO', None))
    if kwargs.has_key('GLACSTNM') and (kwargs['GLACSTNM'] not in (None, '')):
      q = q.filter_by(GLACSTNM = kwargs.pop('GLACSTNM', None))
    q = q.order_by(sa.asc(cls.GLACCONO))
    q = q.order_by(sa.asc(cls.GLACSTNM))
    if opt:
      return q.all()
    else:
      return q.first()

  getObj = classmethod(getObj)

