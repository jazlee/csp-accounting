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
from mvcsvc import *

class EFSYVR(Entity):
  """
  Sys Param
  """
  EFSYCONO  = Field(String(3), label='Comp ID', primary_key=True)
  EFSYUSID  = Field(String(24), label='User ID', primary_key=True)
  EFSYPGID  = Field(String(24), label='Program', primary_key=True)
  EFSYVRID  = Field(String(24), label='Var', primary_key=True)
  EFSYVRV0  = Field(String(48), label='Value 1')
  EFSYVRV1  = Field(String(48), label='Value 2')
  EFSYVRV2  = Field(String(48), label='Value 3')
  EFSYVRV3  = Field(String(48), label='Value 4')
  EFSYVRV4  = Field(String(48), label='Value 5')
  EFSYVRV5  = Field(String(48), label='Value 6')
  EFSYVRV6  = Field(String(48), label='Value 7')
  EFSYVRV7  = Field(String(48), label='Value 8')
  EFSYVRV8  = Field(String(48), label='Value 9')
  EFSYVRV9  = Field(String(48), label='Value 10')
  EFUSAUDT  = Field(Numeric(8,0))
  EFUSAUTM  = Field(Numeric(6,0))
  EFUSAUUS  = Field(String(24))















