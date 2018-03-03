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

class NUMTYP(Entity):
  """
  Numbering type
  """

  NMTPCONO  = Field(String(3), label='Comp. ID', primary_key=True)
  NMTPNOID  = Field(String(4), label='Numbering.Type', primary_key=True)
  NMTPNONM  = Field(String(16), label='Type Name')
  NMTPNODS  = Field(String(48), label='Description')
  NMTPAUDT  = Field(Numeric(8,0), label='Audit date')
  NMTPAUTM  = Field(Numeric(6,0), label='Audit time')
  NMTPAUUS  = Field(String(24), label='Audit user')

