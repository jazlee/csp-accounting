from elixir import *
import sqlalchemy as sa

class GLACCT(Entity):
  GLACCONO    = Field(String(3), primary_key=True, label='Comp No.')
  GLACACID    = Field(String(48), primary_key=True, label='Acct. ID')
  GLACACFM    = Field(String(48), label='Formatted Acct. ID')
  GLACACNM    = Field(String(32), label='Acct. Name')
  GLACACTP    = Field(String(1), label='Acct. Type')
  GLACBLTP    = Field(String(1), label='Balance Type')
  GLACGRTP    = Field(Integer, index=True, label='Group Type')
  GLACACST    = Field(Integer, index=True, label='Status')
  GLACCSST    = Field(Integer)
  GLACALST    = Field(Integer)
  GLACALSR    = Field(String(4))
  GLACSRNM    = Field(String(48))
  GLACALTO    = Field(Integer)
  GLACALPC    = Field(Numeric(7,4))
  GLACSTID    = Field(String(8))
  GLACSTNM    = Field(String(32))
  GLACLCST    = Field(Integer)
  GLACCUCD    = Field(String(3))
  GLACCPTP    = Field(Integer)
  GLACCS01    = Field(String(24))
  GLACCS02    = Field(String(24))
  GLACCS03    = Field(String(24))
  GLACCS04    = Field(String(24))
  GLACCS05    = Field(String(24))
  GLACCS06    = Field(String(24))
  GLACCS07    = Field(String(24))
  GLACCS08    = Field(String(24))
  GLACCS09    = Field(String(24))
  GLACCS10    = Field(String(24))
  GLACAUDT    = Field(Numeric(8,0))
  GLACAUTM    = Field(Numeric(6,0))
  GLACAUUS    = Field(String(24))



