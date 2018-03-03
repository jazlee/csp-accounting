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
import tools

class EFUSRS(Entity):
  """
  User list
  """
  EFUSUSID    = Field(String(24), label='User ID', primary_key=True)
  EFUSUSTP    = Field(String(3), label='USer Type', index=True)
  EFUSPSWD    = Field(String(64), label='Password')
  EFUSFSNM    = Field(String(24), label='First Name')
  EFUSLSNM    = Field(String(24), label='Last Name')
  EFUSEMAD    = Field(String(48), label='Email Addr')
  EFUSDESC    = Field(String(64), label='Desc')
  EFUSCONO    = Field(String(3), label='Comp', index=True)
  EFUSCONM    = Field(String(24), label='Comp Name')
  EFUSDVNO    = Field(String(3), label='Division', index=True)
  EFUSDVNM    = Field(String(24), label='Division')
  EFUSSTAT    = Field(Integer, label='Status')
  EFUSAUDT    = Field(Numeric(8,0), label='Audit Date')
  EFUSAUTM    = Field(Numeric(6,0), label='Audit Time')
  EFUSAUUS    = Field(String(24), label='Audit User')


