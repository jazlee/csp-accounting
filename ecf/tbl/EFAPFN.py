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

class EFAPFN(Entity):
  APIFNCOB    = Field(String(32), primary_key=True)
  APIFNCNM    = Field(String(32), primary_key=True)
  APIFNCDS    = Field(String(64))
  APIFNCST    = Field(Boolean)
  APIFNCTP    = Field(String(1))
  APIFNCSL    = Field(Boolean)
  APIFNCIN    = Field(Boolean)
  APIFNCUP    = Field(Boolean)
  APIFNCDL    = Field(Boolean)
  APIFNCEX    = Field(Boolean)
  APIFAUDT    = Field(Numeric(8,0))
  APIFAUTM    = Field(Numeric(6,0))
  APIFAUUS    = Field(String(24))


