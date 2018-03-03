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

class MSTARE(Entity):
  """
  Area/Region code
  """
  CMARCONO  = Field(String(3), label='Comp. ID', primary_key=True)
  CMARIDCD  = Field(String(6), label='Area Code', primary_key=True)
  CMARIDNM  = Field(String(24), label='Name')
  CMARIDDS  = Field(String(128), label='Desc')
  CMARAUDT  = Field(Numeric(8,0), label='Audit date')
  CMARAUTM  = Field(Numeric(6,0), label='Audit time')
  CMARAUUS  = Field(String(24), label='Audit user')

