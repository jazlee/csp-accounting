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

class EFJBLS(Entity):
  """
  Job list management
  """
  JBLSIDNM    = Field(String(38), primary_key = True)
  JBLSINDT    = Field(Numeric(8,0), index=True)
  JBLSINTM    = Field(Numeric(6,0), index=True)
  JBLSINID    = Field(String(38))
  JBLSRQPG    = Field(String(24))
  JBLSRPDT    = Field(Numeric(8,0))
  JBLSRPTM    = Field(Numeric(6,0))
  JBLSPRPG    = Field(String(24))
  JBLSPRDT    = Field(Numeric(8,0))
  JBLSPRTM    = Field(Numeric(6,0))
  JBLSPRST    = Field(Integer, index=True)
  JBLSMDNM    = Field(String(24))
  JBLSMDID    = Field(String(32))
  JBLSUPDT    = Field(Numeric(8,0))
  JBLSUPTM    = Field(Numeric(6,0))
  JBLSSPRQ    = Field(Integer)
  JBLSSPID    = Field(String(24))
  JBLSSPDT    = Field(Numeric(8,0))
  JBLSSPTM    = Field(Numeric(6,0))
  JBLSPRMS    = Field(String(64))
  JBLSAUDT    = Field(Numeric(8,0))
  JBLSAUTM    = Field(Numeric(6,0))
  JBLSAUUS    = Field(String(24))
