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

class SYSCLJ(Entity):
  """
  System Calendar Job
  """
  SYCLCONO  = Field(String(3), label='Comp. ID', primary_key=True)
  SYCLCLYR  = Field(Numeric(4, 0), label='Year', primary_key=True)
  SYCLCLDS  = Field(String(48), label='Description')
  SYCLCWD0  = Field(Integer, label='Workday')
  SYCLCBD0  = Field(Integer, label='Bankday')
  SYCLCPD0  = Field(Integer, label='Payday')
  SYCLCWD1  = Field(Integer, label='Workday')
  SYCLCBD1  = Field(Integer, label='Bankday')
  SYCLCPD1  = Field(Integer, label='Payday')
  SYCLCWD2  = Field(Integer, label='Workday')
  SYCLCBD2  = Field(Integer, label='Bankday')
  SYCLCPD2  = Field(Integer, label='Payday')
  SYCLCWD3  = Field(Integer, label='Workday')
  SYCLCBD3  = Field(Integer, label='Bankday')
  SYCLCPD3  = Field(Integer, label='Payday')
  SYCLCWD4  = Field(Integer, label='Workday')
  SYCLCBD4  = Field(Integer, label='Bankday')
  SYCLCPD4  = Field(Integer, label='Payday')
  SYCLCWD5  = Field(Integer, label='Workday')
  SYCLCBD5  = Field(Integer, label='Bankday')
  SYCLCPD5  = Field(Integer, label='Payday')
  SYCLCWD6  = Field(Integer, label='Workday')
  SYCLCBD6  = Field(Integer, label='Bankday')
  SYCLCPD6  = Field(Integer, label='Payday')
  SYCLJBID  = Field(String(38), label='Job ID', index=True)
  SYCLAUDT  = Field(Numeric(8,0), label='Audit date')
  SYCLAUTM  = Field(Numeric(6,0), label='Audit time')
  SYCLAUUS  = Field(String(24), label='Audit user')

