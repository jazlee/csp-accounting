#
# Copyright (c) 2009 Cipta Solusi Pratama. All rights reserved.
#
# This product and it's source code is protected by patents, copyright laws and
# international copyright treaties, as well as other intellectual property
# laws and treaties. The product is licensed, not sold.
#
# The source code and sample programs in this package or parts hereof
# as well as the documentation shall not be copied, modified or redistributed
# without permission, explicit or implied, of the author.
#

__author__    = 'Jaimy Azle'
__version__   = '1.0'
__copyright__ = 'Copyright (c) 2009 Cipta Solusi Pratama'

from elixir import *
from sqlalchemy import sql
from sqlalchemy.sql import operators
import sqlalchemy as sa

class CURRAT(Entity):
  """
  Currency rates
  """
  CRRTCONO  = Field(String(3), label='Comp. ID', primary_key=True)
  CRRTCUCD  = Field(String(3), label='Curr. Code', primary_key=True)
  CRRTTPCD  = Field(String(3), label='Rate type', primary_key=True)
  CRRTSRCD  = Field(String(3), label='Src Curr', primary_key=True)
  CRRTRTDT  = Field(Numeric(9,0), label='Rate date', primary_key=True)
  CRRTRTVL  = Field(Numeric(15, 4), label='Rate Value')
  CRRTRTSP  = Field(Numeric(15, 4), label='Spreading')
  CRRTAUDT  = Field(Numeric(8,0), label='Audit date')
  CRRTAUTM  = Field(Numeric(6,0), label='Audit time')
  CRRTAUUS  = Field(String(24), label='Audit user')









