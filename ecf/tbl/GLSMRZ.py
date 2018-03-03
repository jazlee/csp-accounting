from elixir import *
import sqlalchemy as sa

class GLSMRZ(Entity):
  GLSMCONO    = Field(String(3), primary_key=True)
  GLSMACID    = Field(String(48), primary_key=True)
  GLSMFSTP    = Field(Integer, primary_key=True)
  GLSMFSYR    = Field(Numeric(4,0), primary_key=True)
  GLSMSMTP    = Field(Integer, primary_key=True)
  GLSMCUCD    = Field(String(3), primary_key=True)
  GLSMCUTP    = Field(String(1), primary_key=True)
  GLSMCUDC    = Field(Integer)
  GLNTOPBL    = Field(Numeric(18,4))
  GLCROPBL    = Field(Numeric(18,4))
  GLDBOPBL    = Field(Numeric(18,4))
  GLNTPR01    = Field(Numeric(18,4))
  GLCRPR01    = Field(Numeric(18,4))
  GLDBPR01    = Field(Numeric(18,4))
  GLNTPR02    = Field(Numeric(18,4))
  GLCRPR02    = Field(Numeric(18,4))
  GLDBPR02    = Field(Numeric(18,4))
  GLNTPR03    = Field(Numeric(18,4))
  GLCRPR03    = Field(Numeric(18,4))
  GLDBPR03    = Field(Numeric(18,4))
  GLNTPR04    = Field(Numeric(18,4))
  GLCRPR04    = Field(Numeric(18,4))
  GLDBPR04    = Field(Numeric(18,4))
  GLNTPR05    = Field(Numeric(18,4))
  GLCRPR05    = Field(Numeric(18,4))
  GLDBPR05    = Field(Numeric(18,4))
  GLNTPR06    = Field(Numeric(18,4))
  GLCRPR06    = Field(Numeric(18,4))
  GLDBPR06    = Field(Numeric(18,4))
  GLNTPR07    = Field(Numeric(18,4))
  GLCRPR07    = Field(Numeric(18,4))
  GLDBPR07    = Field(Numeric(18,4))
  GLNTPR08    = Field(Numeric(18,4))
  GLCRPR08    = Field(Numeric(18,4))
  GLDBPR08    = Field(Numeric(18,4))
  GLNTPR09    = Field(Numeric(18,4))
  GLCRPR09    = Field(Numeric(18,4))
  GLDBPR09    = Field(Numeric(18,4))
  GLNTPR10    = Field(Numeric(18,4))
  GLCRPR10    = Field(Numeric(18,4))
  GLDBPR10    = Field(Numeric(18,4))
  GLNTPR11    = Field(Numeric(18,4))
  GLCRPR11    = Field(Numeric(18,4))
  GLDBPR11    = Field(Numeric(18,4))
  GLNTPR12    = Field(Numeric(18,4))
  GLCRPR12    = Field(Numeric(18,4))
  GLDBPR12    = Field(Numeric(18,4))
  GLNTPR13    = Field(Numeric(18,4))
  GLCRPR13    = Field(Numeric(18,4))
  GLDBPR13    = Field(Numeric(18,4))
  GLNTPR14    = Field(Numeric(18,4))
  GLCRPR14    = Field(Numeric(18,4))
  GLDBPR14    = Field(Numeric(18,4))
  GLNTPR15    = Field(Numeric(18,4))
  GLCRPR15    = Field(Numeric(18,4))
  GLDBPR15    = Field(Numeric(18,4))
  GLSMAUDT    = Field(Numeric(8,0))
  GLSMAUTM    = Field(Numeric(6,0))
  GLSMAUUS    = Field(String(24))
  
  
  