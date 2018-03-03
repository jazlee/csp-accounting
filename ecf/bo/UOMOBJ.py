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

from procsvc import *
from elixir import *
from validators import *
import datetime as dt
import sqlalchemy as sa
import decimal as dcm
from ecfutil import CurrencyContext
from tbl import MSTUOM, UOMCVT

class UOMOBJ(BusinessObject):
  """
  U/M Collection Object
  """

  def getUMCode(self, cono, umcd):
    cono = '' if cono is None else cono
    umcd = '' if umcd is None else umcd
    obj = MSTUOM.get((cono, umcd))
    if obj:
      return (obj.CMUMUMCD, obj.CMUMUMNM)
    return (None, None)

  def getConvTable(self, umcd, alumcd):
    umcd = '' if umcd is None else umcd
    alumcd = '' if alumcd is None else alumcd
    obj = UOMCVT.get((umcd, alumcd))
    if obj:
      return (obj.CVUMCVFA, obj.CVUMCVFR)
    return (None, None)

  def ConvertValue(self, srcum, dstum, total):
    srcum = '' if srcum is None else srcum
    dstum = '' if dstum is None else dstum
    total = dcm.decimal(0, CurrencyContext) if total is None else \
      dcm.decimal(total, CurrencyContext)
    convinfo = self.getConvTable(srcum, dstum)
    retval = dcm.decimal(0, CurrencyContext)
    cval = dcm.decimal(0, CurrencyContext) if convinfo[0] is None else \
      dcm.decimal(convinfo[0], CurrencyContext)
    dcm.getcontext().prec = 9
    if convinfo[1] == '*':
      return dcm.decimal(total * cval, CurrencyContext)
    elif convinfo[1] == '/':
      if cval == 0:
        raise Exception('Conversion factor is Zero, value could not be devided')
      return dcm.decimal(total / cval, CurrencyContext)
    raise Exception('No conversion could be calculated')

