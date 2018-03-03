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

class FSCFYR(Entity):
  """
  Fiscal Year
  """
  FSYRCONO =  Field(String(3), label='Comp. ID', primary_key=True)
  FSYRTPCD =  Field(String(3), label='Fiscal Type', primary_key=True)
  FSYRFSYR =  Field(Numeric(4, 0), label='Year', primary_key=True)
  FSYRFSNM =  Field(String(16), label='Fiscal Name')
  FSYRPRCT =  Field(Integer, label='Period Count')
  FSYRFSST =  Field(Integer, label='Active')
  FSYRADST =  Field(Integer, label='Accept Adjustment')
  FSYRCLST =  Field(Integer, label='Closed')
  FSYRAUDT  = Field(Numeric(8,0), label='Audit date')
  FSYRAUTM  = Field(Numeric(6,0), label='Audit time')
  FSYRAUUS  = Field(String(24), label='Audit user')



