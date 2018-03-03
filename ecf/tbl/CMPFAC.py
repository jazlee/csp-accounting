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

class CMPFAC(Entity):
  """
  Company Facilities
  """
  CMFAFANO  = Field(String(3), primary_key=True, label='Facility')
  CMFACONO  = Field(String(3), label='Company', nullable=False, index=True)
  CMFADVNO  = Field(String(3), label='Division', nullable=False, index=True)
  CMFACONM  = Field(String(24), label='Company Name')
  CMFADVNM  = Field(String(24), label='Division')
  CMFAFANM  = Field(String(24), label='Name')
  CMFAFADS  = Field(String(48), label='Description')
  CMFAGFNO  = Field(String(3), label='Global facility')
  CMFAGFNM  = Field(String(24), label='Global facility')
  CMFAAUDT  = Field(Numeric(8,0), label='Audit date')
  CMFAAUTM  = Field(Numeric(6,0), label='Audit time')
  CMFAAUUS  = Field(String(24), label='Audit user')

