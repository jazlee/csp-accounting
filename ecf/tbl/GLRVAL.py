from elixir import *
import sqlalchemy as sa
import re
import tools

class GLRVAL(Entity):
  GLRVCONO    = Field(String(3), primary_key=True)
  GLRVRVNM    = Field(String(6), primary_key=True)
  GLRVDESC    = Field(String(32))
  GLRVRTTP    = Field(String(3))
  GLRVSRCE    = Field(String(4))
  GLRVSRLG    = Field(String(2))
  GLRVSRTP    = Field(String(2))
  GLRVGCID    = Field(String(48))
  GLRVGCFM    = Field(String(48))
  GLRVGCNM    = Field(String(32))
  GLRVLCID    = Field(String(48))
  GLRVLCFM    = Field(String(48))
  GLRVLCNM    = Field(String(32))
  GLRVAUDT    = Field(Numeric(8,0))
  GLRVAUTM    = Field(Numeric(6,0))
  GLRVAUUS    = Field(String(24))

  def getObj(cls, opt, **kwargs):
    q = cls.query
    if kwargs.has_key('GLRVCONO') and (kwargs['GLRVCONO'] not in (None, '')):
      q = q.filter_by(GLRVCONO = kwargs.pop('GLRVCONO', None))
    if kwargs.has_key('GLRVRVNM') and (kwargs['GLRVRVNM'] not in (None, '')):
      q = q.filter_by(GLRVRVNM = kwargs.pop('GLRVRVNM', None))
    q = q.order_by(sa.asc(cls.GLRVCONO))
    q = q.order_by(sa.asc(cls.GLRVRVNM))
    if opt:
      return q.all()
    else:
      return q.first()

  getObj = classmethod(getObj)