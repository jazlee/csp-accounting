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

class EFUGRP(Entity):
  """
  User group
  """
  EFUGGRID    = Field(String(24), primary_key=True)
  EFUGUSID    = Field(String(24), primary_key=True)
  EFUGFSNM    = Field(String(24))
  EFUGLSNM    = Field(String(24))
  EFUGAUDT    = Field(Numeric(8,0))
  EFUGAUTM    = Field(Numeric(6,0))
  EFUGAUUS    = Field(String(24))

