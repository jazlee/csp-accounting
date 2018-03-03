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

class CMPLOC(Entity):
  """
  Company Locations
  """

  CMLOLCNO  = Field(String(3), label='Loc', primary_key=True)
  CMLOLCNM  = Field(String(24), label='Name')
  CMLOLCDS  = Field(String(48), label='Description')
  CMLOCONO  = Field(String(3), label='Comp. ID', index=True)
  CMLODVNO  = Field(String(3), label='Division', index=True)
  CMLODVNM  = Field(String(24), label='Division')
  CMLOADR1  = Field(String(48), label='Address')
  CMLOADR2  = Field(String(48), label='Address')
  CMLOADR3  = Field(String(48), label='Address')
  CMLOZIPC  = Field(String(48), label='Zip')
  CMLOARID  = Field(String(6), label='Area')
  CMLOARNM  = Field(String(16), label='Area')
  CMLOSTID  = Field(String(6), label='State')
  CMLOSTNM  = Field(String(16), label='State')
  CMLOCTID  = Field(String(2), label='Country')
  CMLOCTNM  = Field(String(16), label='Country')
  CMLOPHN1  = Field(String(24), label='Phone')
  CMLOPHN2  = Field(String(24), label='Phone')
  CMLOFAX1  = Field(String(24), label='Fax')
  CMLOFAX2  = Field(String(24), label='Fax')
  CMLOXEML  = Field(String(32), label='email')
  CMLOWURL  = Field(String(48), label='URL')
  CMLOAUDT  = Field(Numeric(8,0), label='Audit date')
  CMLOAUTM  = Field(Numeric(6,0), label='Audit time')
  CMLOAUUS  = Field(String(24), label='Audit user')
