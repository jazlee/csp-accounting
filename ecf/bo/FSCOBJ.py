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
from dateutil import relativedelta as rd
from tbl import FSCTYP, FSCFYR, FSCPRD

class FSCOBJ(BusinessObject):
  """
  Fiscal Object Collection
  """
  def findPeriod(self, cono, fstp, trdt):
    """
    Find fiscal period for entered transaction date
    """
    q = FSCPRD.query
    q = q.filter_by(FSPRCONO = cono)
    q = q.filter_by(FSPRTPCD = fstp)
    q = q.filter(sa.and_(
            FSCPRD.FSPRFRDT <= trdt,
            FSCPRD.FSPRTODT >= trdt
          )
        )
    obj = q.first()
    return obj

  def validateFSPeriod(self, cono, fstp, trdt):
    """
    Validate fiscal period for entered transaction date
    """
    obj = self.findPeriod(cono, fstp, trdt)
    if not obj:
      raise Exception('No appropriate fiscal period for current transaction date')
    if (obj.FSPRPRST == 1):
      raise Exception('Fiscal period has been closed')
    return obj

  def validateFSPeriod2(self, cono, fstp, fsyr, fsprd):
    q   = FSCPRD.query
    q   = q.filter_by(FSPRCONO = cono)
    q   = q.filter_by(FSPRTPCD = fstp)
    q   = q.filter_by(FSPRFSYR = fsyr)
    q   = q.filter_by(FSPRPRID = fsprd)
    obj = q.first()
    if not obj:
      raise Exception('No appropriate fiscal period for current transaction date')
    if (obj.FSPRPRST == 1):
      raise Exception('Fiscal period has been closed')
    return obj

  def getNextPeriod(self, cono, fstp, fsyr, fsprd):
    """
    Get next fiscal period for specified year and period
    """
    q   = FSCPRD.query
    q   = q.filter_by(FSPRCONO = cono)
    q   = q.filter_by(FSPRTPCD = fstp)
    q   = q.filter(sa.and_(
              FSCPRD.FSPRFSYR <= fsyr,
              FSCPRD.FSPRPRID >= fsprd
            )
          )
    obj = q.first()
    ret = None
    if obj:
      ret = (obj.FSPRFSYR, obj.FSPRPRID)
    return ret

  def getMinMaxPeriod(self, cono, fstp, fsyr):
    q   = FSCPRD.query
    q   = q.filter_by(FSPRCONO = cono)
    q   = q.filter_by(FSPRTPCD = fstp)
    q   = q.filter_by(FSPRFSYR = fsyr)
    q   = q.order_by(sa.asc(FSCPRD.FSPRTPCD))
    q   = q.order_by(sa.asc(FSCPRD.FSPRFSYR))
    q   = q.order_by(sa.asc(FSCPRD.FSPRPRID))
    obj = q.all()
    ret = None
    lstlen = len(obj)
    if lstlen > 0:
      ret = (obj[:1][0].FSPRPRID, obj[-1:][0].FSPRPRID)
    return ret

  def validateFiscalYear(self, cono, fstp, fsyr, vtyps):
    obj = FSCFYR.get((cono, fstp, fsyr))
    if not obj:
      raise Exception('Fiscal Year has not been registered')
    for vtyp in (vtyps):
      if (vtyp == 1) and (obj.FSYRFSST == 1):
        raise Exception('Could not update transaction on disabled fiscal year')
      if (vtyp == 2) and (obj.FSYRADST == 1):
        raise Exception('Transaction on selected fiscal year is not allowed to be adjusted')
      if (vtyp == 2) and (obj.FSYRCLST == 1):
        raise Exception('Could not update transaction on closed fiscal year')
    return obj

  def getFiscalType(self, cono, fstp):
    obj = FSCTYP.get( (cono, fstp) )
    if obj:
      return (obj.FSTPCONO, obj.FSTPTPCD, obj.FSTPTPNM, obj.FSTPPRCT)
    return (None, None, None, None)

  def getFiscalYear(self, cono, fstp, fsyr):
    obj = FSCFYR.get((cono, fstp, fsyr))
    if obj:
      return (obj.FSYRPRCT, obj.FSYRFSST, obj.FSYRADST, obj.FSYRCLST)
    return (None, None, None, None)

  def createFiscalPeriods(self, cono, fstp, fsyr):
    prdrange = range(1, 13, 1)
    for prd in prdrange:

      dsprd = dt.date(fsyr, prd, 1)
      deprd = dsprd+rd.relativedelta(months=+1, days=-1)

      obprd = FSCPRD.get( (cono, fstp, fsyr, prd))
      appendStatus = False
      if obprd is None:
        obprd = FSCPRD(
          FSPRCONO = cono,
          FSPRTPCD = fstp,
          FSPRFSYR = fsyr,
          FSPRPRID = prd,
          FSPRPRST = 0)
        appendStatus = True
      obprd.FSPRFRDT = dsprd.tointeger()
      obprd.FSPRTODT = deprd.tointeger()
      obprd.FSPRPRNM = "YR%d-PRD%.2d" % (fsyr, prd)
      if appendStatus:
        session.add(obprd)
      else:
        session.update(obprd)

  def deleteFiscalPeriods(self, cono, fstp, fsyr):
    prdrange = range(1, 13, 1)
    for prd in prdrange:
      obprd = FSCPRD.get( (cono, fstp, fsyr, prd))
      if obprd:
        session.delete(obprd)




