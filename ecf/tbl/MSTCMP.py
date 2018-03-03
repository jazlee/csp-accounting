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

class MSTCMP(Entity):
  '''
  Master Company
  '''
  CMCPCONO  = Field(String(3), primary_key=True, nullable=True)
  CMCPCONM  = Field(String(24))
  CMCPCODS  = Field(String(48))
  CMCPADR1  = Field(String(48))
  CMCPADR2  = Field(String(48))
  CMCPADR3  = Field(String(48))
  CMCPZIPC  = Field(String(48))
  CMCPARID  = Field(String(6))
  CMCPARNM  = Field(String(16))
  CMCPSTID  = Field(String(6))
  CMCPSTNM  = Field(String(16))
  CMCPCTID  = Field(String(2))
  CMCPCTNM  = Field(String(16))
  CMCPPHN1  = Field(String(24))
  CMCPPHN2  = Field(String(24))
  CMCPFAX1  = Field(String(24))
  CMCPFAX2  = Field(String(24))
  CMCPXEML  = Field(String(32))
  CMCPWURL  = Field(String(48))
  CMCPMCST  = Field(Integer)
  CMCPCUCD  = Field(String(3))
  CMCPCUNM  = Field(String(16))
  CMCPRTCD  = Field(String(3))
  CMCPRTNM  = Field(String(16))
  CMCPAUDT  = Field(Numeric(8,0))
  CMCPAUTM  = Field(Numeric(6,0))
  CMCPAUUS  = Field(String(24))





