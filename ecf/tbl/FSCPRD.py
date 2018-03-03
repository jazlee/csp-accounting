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

class FSCPRD(Entity):
  """
  Fiscal Periods
  """
  FSPRCONO  = Field(String(3), label='Comp. ID', primary_key=True)
  FSPRTPCD  = Field(String(3), label='Fiscal Type', primary_key=True)
  FSPRFSYR  = Field(Numeric(4, 0), label='Year', primary_key=True)
  FSPRPRID  = Field(Integer, label='Period', primary_key=True)
  FSPRPRNM  = Field(String(16), label='Name')
  FSPRFRDT  = Field(Numeric(9,0), label='Fr. Date', index=True)
  FSPRTODT  = Field(Numeric(9,0), label='To Date', index=True)
  FSPRPRST  = Field(Integer, label='Closed', index=True)
  FSPRAUDT  = Field(Numeric(8,0), label='Audit date')
  FSPRAUTM  = Field(Numeric(6,0), label='Audit time')
  FSPRAUUS  = Field(String(24), label='Audit user')

