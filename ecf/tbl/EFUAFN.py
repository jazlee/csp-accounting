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

class EFUAFN(Entity):
  UAFUSRNM    = Field(String(24), primary_key=True)
  UAFOBJNM    = Field(String(32), primary_key=True)
  UAFFNCNM    = Field(String(32), primary_key=True)
  UAFFNCSL    = Field(Boolean)
  UAFFNCIN    = Field(Boolean)
  UAFFNCUP    = Field(Boolean)
  UAFFNCDL    = Field(Boolean)
  UAFFNCEX    = Field(Boolean)
  UAFFAUDT    = Field(Numeric(8,0))
  UAFFAUTM    = Field(Numeric(6,0))
  UAFFAUUS    = Field(String(24))
