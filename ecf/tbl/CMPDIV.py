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

class CMPDIV(Entity):
  """
  Company division
  """

  CMDVCONO  = Field(String(3), primary_key=True, nullable=True, label='Company')
  CMDVDVNO  = Field(String(3), primary_key=True, nullable=True, label='Division')
  CMDVCONM  = Field(String(24), label='Company Name')
  CMDVDVNM  = Field(String(24), label='Name')
  CMDVDVDS  = Field(String(48), label='Description')
  CMDVADR1  = Field(String(48), label='Address')
  CMDVADR2  = Field(String(48), label='Address')
  CMDVADR3  = Field(String(48), label='Address')
  CMDVZIPC  = Field(String(48), label='Zip')
  CMDVARID  = Field(String(6), label='Area')
  CMDVARNM  = Field(String(16), label='Area')
  CMDVSTID  = Field(String(6), label='State')
  CMDVSTNM  = Field(String(16), label='State')
  CMDVCTID  = Field(String(2), label='Country')
  CMDVCTNM  = Field(String(16), label='Country')
  CMDVPHN1  = Field(String(24), label='Phone')
  CMDVPHN2  = Field(String(24), label='Phone')
  CMDVFAX1  = Field(String(24), label='Fax')
  CMDVFAX2  = Field(String(24), label='Fax')
  CMDVXEML  = Field(String(32), label='email')
  CMDVWURL  = Field(String(48), label='URL')
  CMDVAUDT  = Field(Numeric(8,0), label='Audit date')
  CMDVAUTM  = Field(Numeric(6,0), label='Audit time')
  CMDVAUUS  = Field(String(24), label='Audit user')


