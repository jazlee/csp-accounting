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
from jitutil import *
import datetime as dt
import sqlalchemy as sa
import mvcsvc as mvc
from tbl import MSTCTR, MSTSTA, MSTARE, EFLANG, EFLOCL
from tbl import SYSCAL

@nativeclass
class CMNOBJ(BusinessObject):
  """
  Common Object
  """

  def getSystemCalendar(self, cono, trdt):
    """
    Get system calendar date
    """
    obj = SYSCAL.get((cono, trdt))
    if obj:
      return [obj.SYCLCLYR, obj.SYCLCLMT, obj.SYCLCLDW, obj.SYCLCLWD,
          obj.SYCLCLBD, obj.SYCLCLPD]
    return [None] * 6

  def validateSystemCalendar(self, cono, trdt, vwd = False, vbd = False, vpd = False):
    syscalinfo = self.getSystemCalendar(cono,  trdt)
    if syscalinfo[0] is None:
      raise Exception('The date has not been defined in system calendar')
    if (vwd == True) and (syscalinfo[3] != 1):
      raise Exception('The entered date is not on working day')
    if (vbd == True) and (syscalinfo[4] != 1):
      raise Exception('The entered date is not on bank day')
    if (vpd == True) and (syscalinfo[5] != 1):
      raise Exception('The entered date is not on pay day')
    return syscalinfo

  def getCountry(self, ctcd):
    """
    Get country code and name
    """
    ctcd = '' if ctcd is None else ctcd
    obj = MSTCTR.get( ctcd )
    if obj:
      return (obj.CMCTIDCD, obj.CMCTIDNM)
    return (None, None)

  def getState(self, cono, stcd):
    """
    Get state code and name
    """
    cono = '' if cono is None else cono
    stcd = '' if stcd is None else stcd
    obj = MSTSTA.get( (cono, stcd) )
    if obj:
      return ( obj.CMSTIDCD, obj.CMSTIDNM)
    return (None, None)

  def getArea(self, cono, arcd):
    """
    Get area code and name
    """
    cono = '' if cono is None else cono
    arcd = '' if arcd is None else arcd
    obj = MSTARE.get( (cono, arcd) )
    if obj:
      return (obj.CMARIDCD, obj.CMARIDNM)
    return (None, None)

  def generateInitialTranslation(self, mvcsession, locale, mod, modtype):
    '''Generate initial translation'''
    if (locale in (None, '')) or (mod in (None, '')) or (modtype in (None, '')):
      raise Exception('either locale id, module, or moduletype is null')

    service = mvc.MVCLocalService('__MVCPROXY__')
    mSession= service.getSession(mod)
    sorted_fields = mSession.getFields()
    for name, field in sorted_fields:
      msg = field.label
      if msg not in (None, ''):
        obj = EFLOCL.get( (locale, mod, msg) )
        if not obj:
          if not session.transaction_started():
            session.begin()
          try:
            obj = EFLOCL(
                    EFLCLCCD  = locale,
                    EFLCMDCD  = mod,
                    EFLCMSID  = msg,
                    EFLCMDTP  = modtype,
                    EFLCMSLS  = msg
              )
            self.setAuditFields(obj, mvcsession.cookies['user_name'].encode('utf8'))
            session.save(obj)
            session.commit()
          except:
            session.rollback()
            session.expunge(obj)
            raise

  def initLanguages(self):
    """
    Initialize rate type list
    """
    cnt = EFLANG.query.filter(None).count()
    if cnt == 0:
      obj = EFLANG(
        EFLGLCCD = 'EN-US',
        EFLGLGNM = 'English - US',
        EFLGLGDS = 'English - US'
        )
      self.setAuditFields(obj, 'ADMIN')
      session.add(obj)
      session.commit()
      session.close()

  def initCountries(self):
    """
    Initialize default country list
    """
    cnt = MSTCTR.query.filter(None).count()
    if cnt == 0:
      import pycountry as pctr

      countries = list(pctr.countries)
      for ctr in countries:
        obj = MSTCTR()
        if hasattr(ctr, 'alpha2'):
          obj.CMCTIDCD = ctr.alpha2
        if hasattr(ctr, 'name'):
          obj.CMCTIDNM = ctr.name[:32]
        if hasattr(ctr, 'official_name'):
          obj.CMCTIDDS = ctr.official_name[:48]
        if obj.CMCTIDDS is None:
          obj.CMCTIDDS = obj.CMCTIDNM
        self.setAuditFields(obj, 'ADMIN')
        session.add(obj)
      session.commit()
      session.close()

  def initDatabase(self):
    """
    Initialize database
    """
    self.initCountries()
    self.initLanguages()
