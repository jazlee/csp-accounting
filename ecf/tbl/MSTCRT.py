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

class MSTCRT(Entity):
  '''
  Currency rate
  '''
  CMCTCONO  = Field(String(3), label='Comp. ID', primary_key=True)
  CMCTCUCD  = Field(String(3), label='Curr. Code', primary_key=True)
  CMCTTPCD  = Field(String(3), label='Rate Type', primary_key=True)
  CMCTCRNM  = Field(String(16), label='Curr. Name')
  CMCTDTMT  = Field(String(1), label='Date Match')
  CMCTRTOP  = Field(String(1), label='Rate operation')
  CMCTSRRT  = Field(String(48), label='Source rate')
  CMCTAUDT  = Field(Numeric(8,0), label='Audit date')
  CMCTAUTM  = Field(Numeric(6,0), label='Audit time')
  CMCTAUUS  = Field(String(24), label='Audit user')



