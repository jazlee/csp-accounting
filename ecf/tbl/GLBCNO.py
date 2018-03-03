from elixir import *

#
# G/L Batch Numbering Option
#

class GLBCNO(Entity):
  GLBCNOID  = Field(String(3), primary_key=True)
  GLBCNONM  = Field(String(32))
  GLBCMINO  = Field(Integer)
  GLBCMXNO  = Field(Integer)
  GLBCLSNO  = Field(Integer)
  GLBCAUDT  = Field(Numeric(8, 0))
  GLBCAUTM  = Field(Numeric(6, 0))
  GLBCAUUS  = Field(String(24))

  def getLSNO(cls, noid):
    if noid in (None, ''):
      raise Exception('Default batch option has not been setup properly')
    q = GLBCNO.query
    q = q.filter_by(GLBCNOID = noid)
    obj = q.first()
    if not obj:
      raise Exception('Batch option %s does not exist' % noid)

    ret = None
    if (obj.GLBCMINO > obj.GLBCLSNO):
      ret = obj.GLBCMINO
    else:
      ret = obj.GLBCLSNO + 1
    if ret > obj.GLBCMXNO:
      raise Exception('Maximum number batch has been reached')

    obj.GLBCLSNO = ret
    session.update(obj)

    return ret

  getLSNO = classmethod(getLSNO)






