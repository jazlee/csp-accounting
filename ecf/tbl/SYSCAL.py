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

class SYSCAL(Entity):
  """
  System Calendar
  """

  SYCLCONO  = Field(String(3), label='Comp. ID', primary_key=True)
  SYCLCLDT  = Field(Numeric(8, 0), label='Date', primary_key=True)
  SYCLCLYR  = Field(Numeric(4, 0), label='Year', index=True)
  SYCLCLMT  = Field(Numeric(2, 0), label='Month', index=True)
  SYCLCLDW  = Field(Integer, label='Day of week')
  SYCLCLWD  = Field(Integer, label='Work day')
  SYCLCLBD  = Field(Integer, label='Bank day')
  SYCLCLPD  = Field(Integer, label='Pay day')
  SYCLCLDS  = Field(String(48), label='Description')
  SYCLAUDT  = Field(Numeric(8,0), label='Audit date')
  SYCLAUTM  = Field(Numeric(6,0), label='Audit time')
  SYCLAUUS  = Field(String(24), label='Audit user')