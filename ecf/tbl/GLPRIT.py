from elixir import *

#
# GL Source code profile
#

class GLPRIT(Entity):
  GLITPRID  = Field(String(4), primary_key=True)
  GLITCEID  = Field(String(4), primary_key=True)
  GLITCESR  = Field(String(2))
  GLITCETP  = Field(String(2))
  GLITCENM  = Field(String(32))
  GLITAUDT  = Field(Numeric(8, 0))
  GLITAUTM  = Field(Numeric(6, 0))
  GLITAUUS  = Field(String(24))

  def expandSourceCode(cls, src):
    if src == 'SR-CD':
      raise Exception('Source code should not be an example one')
    if len(src) == 5:
      splitted = src.split('-')
      if (len(splitted) != 2) or (len(splitted[0]) != 2) or (len(splitted[1]) != 2):
        raise Exception('Length of \'SOURCE\' and \'TYPE\' must be in 2 digit code separated by \'-\'.')
      glcode = "%s%s" % tuple(splitted)
      splitted.append(glcode)
      return splitted
    else:
      raise Exception('Source code must be in 5 digit code')
      return None

  expandSourceCode = classmethod(expandSourceCode)





