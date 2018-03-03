from elixir import *
import sqlalchemy as sa
import re
import tools

class GLACRV(Entity):
  GLRVCONO    = Field(String(3), primary_key=True)
  GLRVACID    = Field(String(48), primary_key=True)
  GLRVCUCD    = Field(String(3), primary_key=True)
  GLRVCUNM    = Field(String(16))
  GLRVRVST    = Field(Integer)
  GLRVRVNM    = Field(String(6))
  GLRVAUDT    = Field(Numeric(8,0))
  GLRVAUTM    = Field(Numeric(6,0))
  GLRVAUUS    = Field(String(24))
