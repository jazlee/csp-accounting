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

class NUMSER(Entity):
  """
  Numbering series
  """
  NMSRCONO  = Field(String(3), label='Comp. ID', primary_key=True)
  NMSRNOCD  = Field(String(4), label='Series Code', primary_key=True)
  NMSRFRDT  = Field(Numeric(8, 0), label='From date', primary_key=True)
  NMSRNONM  = Field(String(16), label='Name')
  NMSRMINO  = Field(Integer, label='Min. No')
  NMSRMXNO  = Field(Integer, label='Max. No')
  NMSRLSNO  = Field(Integer, label='last. No')
  NMSRPFCD  = Field(String(3), label='Prefix Used')
  NMSRSFCD  = Field(String(3), label='Suffix used')
  NMSRAUDT  = Field(Numeric(8,0), label='Audit date')
  NMSRAUTM  = Field(Numeric(6,0), label='Audit time')
  NMSRAUUS  = Field(String(24), label='Audit user')