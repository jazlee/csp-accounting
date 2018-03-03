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

class FSCTYP(Entity):
  """
  Fiscal Type
  """
  FSTPCONO  = Field(String(3), label='Comp. ID', primary_key=True)
  FSTPTPCD  = Field(String(3), label='Fiscal Type', primary_key=True)
  FSTPTPNM  = Field(String(24), label='Fiscal Name')
  FSTPTPDS  = Field(String(48), label='Description')
  FSTPPRCT  = Field(Integer, label='Period count')
  FSTPAUDT  = Field(Numeric(8,0), label='Audit date')
  FSTPAUTM  = Field(Numeric(6,0), label='Audit time')
  FSTPAUUS  = Field(String(24), label='Audit user')

