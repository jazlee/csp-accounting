from elixir import *
import sqlalchemy as sa
import re
import tools

class GLALAC(Entity):
  GLALCONO    = Field(String(3), primary_key=True)
  GLALACID    = Field(String(48), primary_key=True)
  GLALALID    = Field(String(48), primary_key=True)
  GLALALFM    = Field(String(48))
  GLALALNM    = Field(String(32))
  GLALALRF    = Field(String(48))
  GLALALPC    = Field(Numeric(7,4))
  GLALAUDT    = Field(Numeric(8,0))
  GLALAUTM    = Field(Numeric(6,0))
  GLALAUUS    = Field(String(24))

  def getObj(cls, opt, **kwargs):
    q = cls.query
    if kwargs.has_key('GLALCONO') and (kwargs['GLALCONO'] not in (None, '')):
      q = q.filter_by(GLALCONO = kwargs.pop('GLALCONO', None))
    if kwargs.has_key('GLALACID') and (kwargs['GLALACID'] not in (None, '')):
      q = q.filter_by(GLALACID = kwargs.pop('GLALACID', None))
    if kwargs.has_key('GLALALID') and (kwargs['GLALALID'] not in (None, 0)):
      q = q.filter_by(GLALALID = kwargs.pop('GLALALID', None))
    q = q.order_by(sa.asc(GLALAC.GLALCONO))
    q = q.order_by(sa.asc(GLALAC.GLALACID))
    q = q.order_by(sa.asc(GLALAC.GLALALID))
    if opt:
      return q.all()
    else:
      return q.first()

  getObj = classmethod(getObj)
