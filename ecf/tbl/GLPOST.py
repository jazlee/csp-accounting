from elixir import *

class GLPOST(Entity):
  GLPOJBID    = Field(String(38), primary_key=True)
  GLPODESC    = Field(String(48))
  GLPOPOMO    = Field(Integer)
  GLPOCONO    = Field(String(3))
  GLPONOID    = Field(String(3))
  GLPOBCFR    = Field(Integer)
  GLPOBCTO    = Field(Integer)
  GLPOPOTP    = Field(Integer)
  GLPOAUDT    = Field(Numeric(8,0))
  GLPOAUTM    = Field(Numeric(6,0))
  GLPOAUUS    = Field(String(24))
  
