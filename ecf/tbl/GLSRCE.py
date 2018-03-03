from elixir import *

#
# GL Source code
#

class GLSRCE(Entity):
  GLSRCEID  = Field(String(4), primary_key=True)
  GLSRCESR  = Field(String(2))
  GLSRCETP  = Field(String(2))
  GLSRCENM  = Field(String(32))
  GLSRAUDT  = Field(Numeric(8, 0))
  GLSRAUTM  = Field(Numeric(6, 0))
  GLSRAUUS  = Field(String(24))

  def getObj(cls, opt, **kwargs):
    q = cls.query
    if kwargs.has_key('GLSRCEID') and (kwargs['GLSRCEID'] not in (None, '')):
      q = q.filter_by(GLSRCEID = kwargs.pop('GLSRCEID', None))
    q = q.order_by(sa.asc(cls.GLSRCEID))
    if opt:
      return q.all()
    else:
      return q.first()

  getObj = classmethod(getObj)



