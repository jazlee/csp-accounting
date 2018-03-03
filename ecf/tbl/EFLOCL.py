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

class EFLOCL(Entity):
  """
  Locale message
  """
  EFLCLCCD  = Field(String(16), primary_key=True, label='Language ID')
  EFLCMDCD  = Field(String(32), primary_key=True, label='Module')
  EFLCMSID  = Field(String(64), primary_key=True, label='Message')
  EFLCMDTP  = Field(Integer, label='Module type')
  EFLCMSLS  = Field(String(250), label='Translation')
  EFLCAUDT  = Field(Numeric(8, 0))
  EFLCAUTM  = Field(Numeric(6, 0))
  EFLCAUUS  = Field(String(24))