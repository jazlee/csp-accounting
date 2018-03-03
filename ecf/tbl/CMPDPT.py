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

class CMPDPT(Entity):
  """
  Departments
  """

  CMDPCONO  = Field(String(3), label='Comp', primary_key=True)
  CMDPDVNO  = Field(String(3), label='Div', primary_key=True)
  CMDPDPNO  = Field(String(6), label='Dept', primary_key=True)
  CMDPDPNM  = Field(String(24), label='Name')
  CMDPDPDS  = Field(String(48), label='Description')
  CMDPFANO  = Field(String(3), label='Facility', index=True)
  CMDPFANM  = Field(String(24), label='Facility')
  CMDPLCNO  = Field(String(3), label='Location', index=True)
  CMDPLCNM  = Field(String(24), label='Location')
  CMDPAUDT  = Field(Numeric(8,0), label='Audit date')
  CMDPAUTM  = Field(Numeric(6,0), label='Audit time')
  CMDPAUUS  = Field(String(24), label='Audit user')


