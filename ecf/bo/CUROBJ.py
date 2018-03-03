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
from tbl import MSTCUR, MSTCRT, CURRAT, MSTXRT

class CUROBJ(BusinessObject):
  """
  Currency Utilities Object
  """
  def getCurrency(self, cucd):
    """
    Get currency code, and name
    """
    obj = MSTCUR.get( cucd )
    if obj:
      return (obj.CMCRCUCD, obj.CMCRCUNM)
    return (None, None)

  def getRateType(self, crtp):
    """
    Get rate type code, and name
    """
    obj = MSTXRT.get( crtp )
    if obj:
      return (obj.CMRTTPCD, obj.CMRTTPNM)
    retun (None, None)

  def getExchangeRule(self, cono, cucd, crtp):
    """
    Get exchange rule for currency
    @param: cono, cucd, crtp
    """
    obj = MSTCRT.get((cono, cucd, crtp))
    if obj:
      return (obj.CMCTCUCD, obj.CMCTTPCD, obj.CMCTCRNM, obj.CMCTDTMT, obj.CMCTRTOP, obj.CMCTSRRT)
    return (None, None, None, None, None, None)

  def getRateDate(self, cono, cucd, crtp, chcd, rtdt):
    rule = self.getExchangeRule(cono, cucd, crtp)
    if rtdt is not None:
      if rule[3] not in ('<', '=', '>'):
        raise Exception('Date match searching unknown')
      q = CURRAT.query
      q = q.filter_by(CRRTCONO = cono)
      q = q.filter_by(CRRTCUCD = rule[0])
      q = q.filter_by(CRRTTPCD = rule[1])
      q = q.filter_by(CRRTSRCD = chcd)
      if rule[3] == '<':
        q = q.filter(CURRAT.CRRTRTDT <= rtdt)
        q = q.order_by(sa.asc(CURRAT.CRRTCUCD))
        q = q.order_by(sa.asc(CURRAT.CRRTTPCD))
        q = q.order_by(sa.asc(CURRAT.CRRTSRCD))
        q = q.order_by(sa.desc(CURRAT.CRRTRTDT))
      elif rule[3] == '=':
        q = q.filter(CURRAT.CRRTRTDT == rtdt)
        q = q.order_by(sa.asc(CURRAT.CRRTCUCD))
        q = q.order_by(sa.asc(CURRAT.CRRTTPCD))
        q = q.order_by(sa.asc(CURRAT.CRRTSRCD))
        q = q.order_by(sa.asc(CURRAT.CRRTRTDT))
      elif rule[3] == '>':
        q = q.filter(CURRAT.CRRTRTDT >= rtdt)
        q = q.order_by(sa.asc(CURRAT.CRRTCUCD))
        q = q.order_by(sa.asc(CURRAT.CRRTTPCD))
        q = q.order_by(sa.asc(CURRAT.CRRTSRCD))
        q = q.order_by(sa.asc(CURRAT.CRRTRTDT))
      obj = q.first()
      if obj:
        return (rule[0], rule[1], rule[2], rule[3], rule[4], rule[5], obj.CRRTRTVL, obj.CRRTRTSP, obj.CRRTRTDT)
    return (rule[0], rule[1], rule[2], rule[3], rule[4], rule[5], None, None, None)

  def convertRate(self, rtval, rtop, amount):

    rtval = 1 if rtval is None else rtval
    amount = 0 if amount is None else amount
    rtop = '*' if rtop is None else rtop

    dcm.getcontext().prec = 9
    namount = dcm.Decimal(amount, CurrencyContext)
    nrtval = dcm.Decimal(rtval, CurrencyContext)
    if rtop == '*':
      return dcm.Decimal(namount * nrtval)
    elif rtop == '/':
      return dcm.Decimal(namount / nrtval)
    return namount

  def initCurrencies(self):
    """
    Initialize currency list
    """
    cnt = MSTCUR.query.filter(None).count()
    if cnt == 0:
      import pycountry as pctr

      currencies = list(pctr.currencies)
      for curr in currencies:
        obj = MSTCUR()
        if hasattr(curr, 'letter'):
          obj.CMCRCUCD = curr.letter
        if hasattr(curr, 'name'):
          obj.CMCRCUNM = curr.name[:24]
          obj.CMCRCUDS = curr.name[:48]
        self.setAuditFields(obj, 'ADMIN')
        session.add(obj)
      session.commit()
      session.close()

  def initRateType(self):
    """
    Initialize rate type list
    """
    cnt = MSTXRT.query.filter(None).count()
    if cnt == 0:
      obj = MSTXRT(
        CMRTTPCD = 'DAI',
        CMRTTPNM = 'Daily rate',
        CMRTTPDS = 'Daily rate'
        )
      self.setAuditFields(obj, 'ADMIN')
      session.add(obj)
      session.commit()
      session.close()

  def initDatabase(self):
    self.initCurrencies()
    self.initRateType()


