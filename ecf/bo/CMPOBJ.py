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
import ecfpool
from sqlalchemy.orm.attributes import InstrumentedAttribute
from tbl import MSTCMP, CMPDIV, CMPFAC, CMPLOC, CMPDPT, CMPSDP

class CMPOBJ(BusinessObject):
  """
  Company Utility Object
  """

  def updateCOMPCache(self, obj):
    pool = ecfpool.getCachePool()
    cmp_pool = pool.getCOMPDict(obj.CMCPCONO)
    if cmp_pool is None:
      cmp_pool = {}
    for key in MSTCMP.__dict__.iterkeys():
      if isinstance(MSTCMP.__dict__[key], InstrumentedAttribute):
        cmp_pool[key] = getattr(obj, key, None)
    pool.setCOMPDict(obj.CMCPCONO, cmp_pool)

  def removeCOMPCache(self, obj):
    pool = ecfpool.getCachePool()
    pool.delCOMPDict(obj.CMCPCONO)


  def getCompany(self, cono):
    """
    Get company code, name, default currency, and default rate used
    """
    cono = cono if cono else ''
    pool = ecfpool.getCachePool()
    cmp_cache = pool.getCOMPDict(cono)
    if cmp_cache is None:
      obj = MSTCMP.get( cono )
      if obj:
        self.updateCOMPCache(obj)
        return (obj.CMCPCONO, obj.CMCPCONM, obj.CMCPCUCD, obj.CMCPRTCD)
      else:
        return (None, None, None, None)
    return (cmp_cache['CMCPCONO'], cmp_cache['CMCPCONM'], cmp_cache['CMCPCUCD'], cmp_cache['CMCPRTCD'])

  def updateDIVICache(self, obj):
    pool = ecfpool.getCachePool()
    cmp_pool = pool.getDIVDict(obj.CMDVCONO, obj.CMDVDVNO)
    if cmp_pool is None:
      cmp_pool = {}
    for key in CMPDIV.__dict__.iterkeys():
      if isinstance(CMPDIV.__dict__[key], InstrumentedAttribute):
        cmp_pool[key] = getattr(obj, key, None)
    pool.setDIVDict(obj.CMDVCONO, obj.CMDVDVNO, cmp_pool)

  def removeDIVICache(self, obj):
    pool = ecfpool.getCachePool()
    pool.delDIVDict(obj.CMDVCONO, obj.CMDVDVNO)

  def getDivision(self, cono, divi):
    """
    Get division company code, comp. name, div. code, and div. name
    """
    cono = cono if cono else ''
    divi = divi if divi else ''
    cmpno, cmpnm, divino, divinm = (None, None, None, None)
    pool = ecfpool.getCachePool()
    divi_cache = pool.getDIVDict(cono, divi)
    if divi_cache is None:
      obj = CMPDIV.get( (cono, divi) )
      if obj:
        self.updateDIVICache(obj)
        cmpno, cmpnm, divino, divinm = (obj.CMDVCONO, obj.CMDVCONM, obj.CMDVDVNO, obj.CMDVDVNM)
    else:
      cmpno, cmpnm, divino, divinm = (divi_cache['CMDVCONO'],
          divi_cache['CMDVCONM'],
          divi_cache['CMDVDVNO'],
          divi_cache['CMDVDVNM'])
    cmpno, cmpnm, tmp1, tmp2 = self.getCompany(cmpno)
    return (cmpno, cmpnm, divino, divinm)

  def getFacility(self, fano):
    """
    Get division company code, comp. name, div. code, div. name, fac. code, and fac.name
    """
    facino, facinm, cmpno, cmpnm, divino, divinm = (None, None, None, None, None, None)
    obj = CMPFAC.get( fano )
    if obj:
      facino, facinm, cmpno, cmpnm, divino, divinm = (obj.CMFAFANO, obj.CMFAFANM, \
          obj.CMFACONO, obj.CMFACONM, obj.CMFADVNO, obj.CMFADVNM)
    cmpno, cmpnm, divino, divinm = self.getDivision( cmpno, divino )
    return (cmpno, cmpnm, divino, divinm, facino, facinm)

  def getLocation(self, locno):
    obj = CMPLOC.get(locno)
    if obj:
      locinfo = list(self.getDivision(obj.CMLOCONO, obj.CMLODVNO))
      locinfo.extend([obj.CMLOLCNO, obj.CMLOLCNM])
      return tuple(locinfo)
    return tuple([None] * 6)

  def getDepartment(self, cono, dvno, dpno):
    cono, dvno, dpno = [val if val != None else '' for val in [cono, dvno, dpno]]
    obj = CMPDPT.get((cono, dvno, dpno))
    if obj:
      return (obj.CMDPCONO, obj.CMDPDVNO, obj.CMDPDPNO, obj.CMDPDPNM)
    return tuple([None] * 4)

  def getSubDepartment(self, cono, dvno, sdpno):
    cono, dvno, sdpno = [val if val != None else '' for val in [cono, dvno, sdpno]]
    obj = CMPSDP.get((cono, dvno, sdpno))
    if obj:
      return (obj.CMSBCONO, obj.CMSBDVNO, obj.CMSBDPNO, obj.CMSBDPNM, obj.CMSBSBNO, obj.CMSBSBNM)
    return tuple([None] * 6)

  def validateCompany(self, cono):
    coinfo = self.getCompany(cono)
    validators.NotEmpty(messages={'empty':'Company has not been setup properly'}).to_python(coinfo[0])

  def validateDivision(self, cono, divi):
    dvinfo = self.getDivision(cono, divi)
    validators.NotEmpty(messages={'empty':'Company and or division has not been setup properly'}).to_python(dvinfo[0])

  def initCompany(self):
    """
    Initialize default company
    """
    proxy = self.getBusinessObjectProxy()
    cnt = MSTCMP.query.filter(None).count()
    if cnt == 0:
      curobj = proxy.getObject('CUROBJ')
      curinfo = curobj.getCurrency('USD')
      rtinfo = curobj.getRateType('DAI')
      obj = MSTCMP(
        CMCPCONO = '',
        CMCPCONM = 'Blank Company',
        CMCPCODS = 'Blank Company Configuration',
        CMCPMCST = 1,
        CMCPCUCD = curinfo[0],
        CMCPCUNM = curinfo[1],
        CMCPRTCD = rtinfo[0],
        CMCPRTNM = rtinfo[1])

      self.setAuditFields(obj, 'ADMIN')
      session.add(obj)
      session.commit()
      session.close()

  def initDatabase(self):
    """
    Initialize database
    """
    self.initCompany()











