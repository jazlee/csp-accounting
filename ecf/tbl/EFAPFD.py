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

class EFAPFD(Entity):
  APIFLDOB    = Field(String(32), primary_key=True)
  APIFLDFN    = Field(String(32), primary_key=True)
  APIFLDNM    = Field(String(32), primary_key=True)
  APIFLDDS    = Field(String(64))
  APIFLDIO    = Field(Integer)
  APIFLDTP    = Field(String(16))
  APIFLDLN    = Field(Integer)
  APIFLDPR    = Field(Integer)
  APIFLDDC    = Field(Integer)
  APIFLDRQ    = Field(Boolean)
  APIFAUDT    = Field(Numeric(8,0))
  APIFAUTM    = Field(Numeric(6,0))
  APIFAUUS    = Field(String(24))