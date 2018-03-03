from elixir import *

#
# GL Source code profile
#

class GLPRJN(Entity):
  GLPRPRID  = Field(String(4), primary_key=True)
  GLPRPRNM  = Field(String(48))
  GLPRAUDT  = Field(Numeric(8, 0))
  GLPRAUTM  = Field(Numeric(6, 0))
  GLPRAUUS  = Field(String(24))

