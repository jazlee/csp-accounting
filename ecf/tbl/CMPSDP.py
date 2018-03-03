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

class CMPSDP(Entity):
  """
  Sub-Department
  """
  CMSBCONO  = Field(String(3), label='Comp', primary_key=True)
  CMSBDVNO  = Field(String(3), label='Div', primary_key=True)
  CMSBSBNO  = Field(String(4), label='Sub-Dept', primary_key=True)
  CMSBDPNO  = Field(String(3), label='Dept', index=True)
  CMSBDPNM  = Field(String(24), label='Dept')
  CMSBSBNM  = Field(String(24), label='Name')
  CMSBSBDS  = Field(String(48), label='Description')
  CMSBAUDT  = Field(Numeric(8,0), label='Audit date')
  CMSBAUTM  = Field(Numeric(6,0), label='Audit time')
  CMSBAUUS  = Field(String(24), label='Audit user')