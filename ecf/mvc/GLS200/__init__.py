"""
G/L Journal Entry
"""

__author__    = 'Jaimy Azle'
__version__   = '1.0'
__copyright__ = 'Copyright (c) 2008 Jaimy Azle'

from mvcsvc import *
from elixir import *
import datetime as dt
from validators import *
import sqlalchemy as sa
import decimal as dcm
from ecfutil import CurrencyContext
from tbl import GLJHDR, GLJITM, GLBCTL, GLSOPT, EFUSRS


class GLS200(MVCController):
  """
  G/L Journal Entry.
  """
  _description = 'G/L Journal Entry'
  _supported_functions = (MVCFuncSelect, MVCFuncNew, MVCFuncOpen, MVCFuncShow, MVCFuncDelete)

  GLJHBCID    = MVCField(MVCTypeList + MVCTypeField + MVCTypeParam, String(6), label='Batch No.', browseable=True, synchronized=True)
  GLJHBCDS    = MVCField(MVCTypeField, String(32), label='Batch Desc.', enabled=False )
  GLJHJEID    = MVCField(MVCTypeList + MVCTypeField, String(6), label='Trans. No.', enabled=False )
  GLJHJEDT    = MVCField(MVCTypeList + MVCTypeField, Date, label='Trans. Date', synchronized=True)
  GLJHFSYR    = MVCField(MVCTypeField, Integer(), label='Year', browseable=True)
  GLJHFSPR    = MVCField(MVCTypeField, Integer(), label='Period', browseable=True)
  GLJHJEDS    = MVCField(MVCTypeList + MVCTypeField, String(48), label='Description')
  GLJHJERV    = MVCField(MVCTypeField, Integer(), label='Reversed')
  GLJHDTCR    = MVCField(MVCTypeField, Date, label='Created', enabled=False)
  GLJHDTED    = MVCField(MVCTypeField, Date, label='Edited', enabled=False)
  GLJHSRLG    = MVCField(MVCTypeList + MVCTypeField, String(2), label='Src', enabled=False)
  GLJHSRTP    = MVCField(MVCTypeList + MVCTypeField, String(2), label='Typ', enabled=False)
  GLJHNTDB    = MVCField(MVCTypeList + MVCTypeField, Numeric(18,4), label='Debit', enabled=False)
  GLJHNTCR    = MVCField(MVCTypeList + MVCTypeField, Numeric(18,4), label='Credit', enabled=False)
  GLJHJEST    = MVCField(MVCTypeList + MVCTypeField, Integer(), label='Status', enabled=False,
    choices =
      {
        'Editable':1,
        'Non-Editable':2
      })

  def initView(self, mvcsession):
    mvcsession.selectFunction = MVCExtFunction('xxx', 'GLS201', params = {'GLJIBCID':'%f:GLJHBCID', 'GLJIJEID':'%f:GLJHJEID'}, autoSelect=False)
    mvcsession.extFunctions = ( MVCExtFunction('Journal Items', 'GLS201', params = {'GLJIBCID':'%f:GLJHBCID', 'GLJIJEID':'%f:GLJHJEID'}), )
    return mvcsession

  def lookupView(self, mvcsession, fieldName):
    ret = MVCLookupDef('','')
    if fieldName == 'GLJHBCID':
      ret.svcname = 'GLS100'
      ret.retfield = 'GLBCLSID'

    if fieldName in ('GLJHFSYR', 'GLJHFSPR'):
      proxy = self.getBusinessObjectProxy()
      usrobj = proxy.getObject('USROBJ')
      glsobj = proxy.getObject('GLSOBJ')
      info = usrobj.retrieveUserInfoDict(mvcsession)
      cono = info['USRCONO']
      glopt = glsobj.getGLOpt(cono)
      optvalue = '%v:'+ '%d' % glopt['GLOPFSTP']

      if fieldName == 'GLJHFSYR':
        ret.svcname = 'CMN150'
        ret.params = {'SYFSFSTP': optvalue}
        ret.retfield = 'SYFSFSYR'

      if fieldName == 'GLJHFSPR':
        ret.svcname = 'CMN155'
        ret.params = {'SYFPFSYR':'%f:GLJHFSYR', 'SYFPFSTP':optvalue}
        ret.retfield = 'SYFPPRID'

    return ret

  def synchronizeData(self, mvcsession, fieldName, fieldType):
    proxy = self.getBusinessObjectProxy()
    usrobj = proxy.getObject('USROBJ')
    glsobj = proxy.getObject('GLSOBJ')
    info = usrobj.retrieveUserInfoDict(mvcsession)
    cono = info['USRCONO']
    glopt = glsobj.getGLOpt(cono)

    if not mvcsession.entryDataset.IsEmpty:
      fields = mvcsession.entryDataset.FieldsAsDict()
      if (fieldName == 'GLJHBCID') and \
         (fields['GLJHBCID'] not in (None, '')):
        obj = GLBCTL.getObj(False, GLBCCONO = cono, GLBCNOID = glopt['GLOPBCNO'], GLBCLSID = fields['GLJHBCID'])
        if not obj:
          raise Exception('Batch no %s could not be found')
        mvcsession.entryDataset.Edit()
        mvcsession.entryDataset.SetFieldValue('GLJHBCDS', obj.GLBCNODS)
        mvcsession.entryDataset.Post()

      if (fieldName == 'GLJHJEDT') and \
         (fields['GLJHJEDT'] not in (None, 0)):
        fscobj = proxy.getObject('FSCOBJ')
        obj = fscobj.findPeriod(cono, glopt['GLOPFSTP'], fields['GLJHJEDT'].date().tointeger())
        if not obj:
          raise Exception('Fiscal periods has not been setup properly')
        mvcsession.entryDataset.Edit()
        mvcsession.entryDataset.SetFieldValue('GLJHFSYR', obj.SYFPFSYR)
        mvcsession.entryDataset.SetFieldValue('GLJHFSPR', obj.SYFPPRID)
        mvcsession.entryDataset.Post()

    return mvcsession

  def openView(self, mvcsession):
    proxy = self.getBusinessObjectProxy()
    usrobj = proxy.getObject('USROBJ')
    glsobj = proxy.getObject('GLSOBJ')
    if not mvcsession.paramDataset.IsEmpty:
      fields = mvcsession.paramDataset.FieldsAsDict()
      info = usrobj.retrieveUserInfoDict(mvcsession)
      cono = info['USRCONO']
      glopt = glsobj.getGLOpt(cono)
      if fields['GLJHBCID'] not in (None, ''):
        objs = GLJHDR.getObj(True, GLJHCONO = cono, GLJHNOID = glopt['GLOPBCNO'],
                  GLJHBCID = fields['GLJHBCID'])
        for obj in objs:
          mvcsession.listDataset.CopyFromORM(
            'GLJHBCID;GLJHJEDT;GLJHJEDS;GLJHSRLG;GLJHSRTP;GLJHNTDB;GLJHNTCR;GLJHJEST',
            'GLJHBCID;GLJHJEDT;GLJHJEDS;GLJHSRLG;GLJHSRTP;GLJHNTDB;GLJHNTCR;GLJHJEST',
            obj
          )
          mvcsession.listDataset.Edit()
          mvcsession.listDataset.SetFieldValue('GLJHBCID', '%.6d' % obj.GLJHBCID)
          mvcsession.listDataset.SetFieldValue('GLJHJEID', '%.6d' % obj.GLJHJEID)
          mvcsession.listDataset.Post()

    return mvcsession

  def retrieveData(self, mvcsession):
    proxy = self.getBusinessObjectProxy()
    usrobj = proxy.getObject('USROBJ')
    glsobj = proxy.getObject('GLSOBJ')
    info = usrobj.retrieveUserInfoDict(mvcsession)
    cono = info['USRCONO']
    glopt = glsobj.getGLOpt(cono)

    if mvcsession.execType == MVCExecAppend:
      fields = mvcsession.paramDataset.FieldsAsDict()
      bcid = None
      bcds = None
      if fields['GLJHBCID'] not in (None, ''):
        obj = GLBCTL.getObj(False, GLBCCONO = cono, GLBCNOID = glopt['GLOPBCNO'], GLBCLSID = fields['GLJHBCID'])
        if not obj:
          raise Exception('Batch no %s could not be found')
        # batch status not in (Open, ERROR)
        if obj.GLBCBCST not in (1, 5):
          raise Exception('Could not create a new journal for this batch %s ' % fields['GLJHBCID'])
        bcid = '%.6d' % obj.GLBCLSID
        bcds = obj.GLBCNODS
      mvcsession.entryDataset.Append()
      mvcsession.entryDataset.SetFieldValue('GLJHBCID', bcid)
      mvcsession.entryDataset.SetFieldValue('GLJHJEID', None)
      mvcsession.entryDataset.SetFieldValue('GLJHJEDT', None)
      mvcsession.entryDataset.SetFieldValue('GLJHJEDS', None)
      mvcsession.entryDataset.SetFieldValue('GLJHSRLG', 'GL')
      mvcsession.entryDataset.SetFieldValue('GLJHSRTP', 'JE')
      mvcsession.entryDataset.SetFieldValue('GLJHNTDB', 0)
      mvcsession.entryDataset.SetFieldValue('GLJHNTCR', 0)
      mvcsession.entryDataset.SetFieldValue('GLJHJEST', 1)
      mvcsession.entryDataset.SetFieldValue('GLJHFSYR', None)
      mvcsession.entryDataset.SetFieldValue('GLJHFSPR', None)
      mvcsession.entryDataset.SetFieldValue('GLJHBCDS', bcds)
      mvcsession.entryDataset.SetFieldValue('GLJHJERV', 0)
      mvcsession.entryDataset.SetFieldValue('GLJHDTCR', dt.date.today().tointeger())
      mvcsession.entryDataset.SetFieldValue('GLJHDTED', dt.date.today().tointeger())
      mvcsession.entryDataset.Post()
    else:
      fields = mvcsession.listDataset.FieldsAsDict()
      obj = GLJHDR.getObj(False, GLJHCONO = cono,
                GLJHNOID = glopt['GLOPBCNO'],
                GLJHBCID = int(fields['GLJHBCID']),
                GLJHJEID = int(fields['GLJHJEID']))
      if not obj:
        raise Exception('Selected record could not be found')

      if mvcsession.execType in (MVCExecShow, MVCExecEdit, MVCExecDelete):
        mvcsession.entryDataset.CopyFromORM(
          'GLJHJEDT;GLJHJEDS;GLJHSRLG;GLJHSRTP;GLJHNTDB;GLJHNTCR;'\
          'GLJHJEST;GLJHFSYR;GLJHFSPR;GLJHBCDS;GLJHJERV;GLJHDTCR;GLJHDTED',
          'GLJHJEDT;GLJHJEDS;GLJHSRLG;GLJHSRTP;GLJHNTDB;GLJHNTCR;'\
          'GLJHJEST;GLJHFSYR;GLJHFSPR;GLJHBCDS;GLJHJERV;GLJHDTCR;GLJHDTED',
          obj
        )
        mvcsession.entryDataset.Edit()
        mvcsession.entryDataset.SetFieldValue('GLJHBCID', '%.6d' % obj.GLJHBCID)
        mvcsession.entryDataset.SetFieldValue('GLJHJEID', '%.6d' % obj.GLJHJEID)
        mvcsession.entryDataset.Post()

        if mvcsession.execType == MVCExecEdit:
          mvcsession.fieldDefs.GLJHBCID.enabled = False
          bctl = GLBCTL.getObj(False, GLBCCONO = cono, GLBCNOID = glopt['GLOPBCNO'], GLBCLSID = fields['GLJHBCID'])
          if bctl:
            # batch status not in (Open, ERROR)
            if bctl.GLBCBCST not in (1, 5):
              mvcsession.fieldDefs.GLJHJEDT.enabled = False
              mvcsession.fieldDefs.GLJHJEDS.enabled = False
              mvcsession.fieldDefs.GLJHFSYR.enabled = False
              mvcsession.fieldDefs.GLJHFSPR.enabled = False
              mvcsession.fieldDefs.GLJHJERV.enabled = False

      if mvcsession.execType == MVCExecCopy:
        mvcsession.entryDataset.CopyFromORM(
          'GLJHJEDS;GLJHBCDS;GLJHJERV',
          'GLJHJEDS;GLJHBCDS;GLJHJERV',
          obj
        )
        mvcsession.entryDataset.Edit()
        mvcsession.entryDataset.SetFieldValue('GLJHBCID', '%.6d' % obj.GLJHBCID)
        mvcsession.entryDataset.SetFieldValue('GLJHFSYR', None)
        mvcsession.entryDataset.SetFieldValue('GLJHFSPR', None)
        mvcsession.entryDataset.SetFieldValue('GLJHJEDT', None)
        mvcsession.entryDataset.SetFieldValue('GLJHDTCR', dt.date.today().tointeger())
        mvcsession.entryDataset.SetFieldValue('GLJHDTED', dt.date.today().tointeger())
        mvcsession.entryDataset.SetFieldValue('GLJHSRLG', 'GL')
        mvcsession.entryDataset.SetFieldValue('GLJHSRTP', 'JE')
        mvcsession.entryDataset.SetFieldValue('GLJHJEST', 1)
        mvcsession.entryDataset.SetFieldValue('GLJHJEED', 1)
        mvcsession.entryDataset.SetFieldValue('GLJHNTDB', 0)
        mvcsession.entryDataset.SetFieldValue('GLJHNTCR', 0)
        mvcsession.entryDataset.Post()
    return mvcsession

  def postData(self, mvcsession):
    fields = mvcsession.entryDataset.FieldsAsDict()
    proxy = self.getBusinessObjectProxy()
    usrobj = proxy.getObject('USROBJ')
    glsobj = proxy.getObject('GLSOBJ')

    validators.NotEmpty(messages={'empty': 'Batch number must not empty'}).to_python(fields['GLJHBCID'])
    validators.NotEmpty(messages={'empty': 'Transaction date must not empty'}).to_python(fields['GLJHJEDT'])
    validators.NotEmpty(messages={'empty': 'Fiscal year must not empty'}).to_python(fields['GLJHFSYR'])
    validators.NotEmpty(messages={'empty': 'Fiscal period must not empty'}).to_python(fields['GLJHFSPR'])
    validators.NotEmpty(messages={'empty': 'Journal description must not empty'}).to_python(fields['GLJHJEDS'])
    info = usrobj.retrieveUserInfoDict(mvcsession)
    cono = info['USRCONO']
    glopt = glsobj.getGLOpt(cono)
    td = dt.datetime.now()

    if (mvcsession.execType in (MVCExecAppend, MVCExecCopy)):
      bctl = GLBCTL.getObj(False, GLBCCONO = cono, GLBCNOID = glopt['GLOPBCNO'], GLBCLSID = fields['GLJHBCID'])
      if not bctl:
        raise Exception('Batch no %s could not be found')
      # batch status not in (Open, ERROR)
      if bctl.GLBCBCST not in (1, 4, 5):
        raise Exception('Could not create a new journal for this batch %s ' % fields['GLJHBCID'])
      fsyr = CSYFSC.validateFiscalYear(glopt['GLOPFSTP'], fields['GLJHFSYR'], (1,))
      fsprd= CSYFSP.validateFSPeriod2(glopt['GLOPFSTP'], fields['GLJHFSYR'], fields['GLJHFSPR'])
      bcid = '%.6d' % bctl.GLBCLSID
      bcds = bctl.GLBCNODS
      lsbc = GLJHDR.getLSNO(bctl)
      lsno = lsbc[0]
      bctl = lsbc[1]
      rec = GLJHDR(
          GLJHCONO = cono,
          GLJHNOID = glopt['GLOPBCNO'],
          GLJHBCID = bctl.GLBCLSID,
          GLJHJEID = lsno,
          GLJHBCDS = fields['GLJHBCDS'],
          GLJHFSYR = fields['GLJHFSYR'],
          GLJHFSPR = fields['GLJHFSPR'],
          GLJHJEDS = fields['GLJHJEDS'],
          GLJHJEDT = fields['GLJHJEDT'].date().tointeger(),
          GLJHJERV = fields['GLJHJERV'],
          GLJHDTCR = td.date().tointeger(),
          GLJHDTED = td.date().tointeger(),
          GLJHSRLG = 'GL',
          GLJHSRTP = 'JE',
          GLJHJEST = 1,
          GLJHJEED = 1,
          GLJHLSTR = 0,
          GLJHNTDB = 0,
          GLJHNTCR = 0,
          GLJHAUDT = td.date().tointeger(),
          GLJHAUTM = td.time().tointeger(),
          GLJHAUUS = mvcsession.cookies['user_name'].encode('utf8')
        )
      if not session.transaction_started():
        session.begin()
      try:
        session.save(rec)
        session.commit()
      except:
        session.rollback()
        session.expunge(rec)
        raise
    if (mvcsession.execType in (MVCExecEdit, MVCExecDelete)):
      fsobj = CSYFSC.validateFiscalYear(glopt['GLOPFSTP'], fields['GLJHFSYR'], (1,))
      fsprd = CSYFSP.validateFSPeriod2(glopt['GLOPFSTP'], fields['GLJHFSYR'], fields['GLJHFSPR'])
      bctl = GLBCTL.getObj(False, GLBCCONO = cono,
                                  GLBCNOID = glopt['GLOPBCNO'],
                                  GLBCLSID = fields['GLJHBCID'])
      if not bctl:
        raise Exception('Batch no %s could not be found')

      obj = GLJHDR.getObj(False, GLJHCONO = cono,
                GLJHNOID = glopt['GLOPBCNO'],
                GLJHBCID = int(fields['GLJHBCID']),
                GLJHJEID = int(fields['GLJHJEID']))
      if not obj:
        raise Exception('Selected record could not be found')

      if (mvcsession.execType == MVCExecEdit):
        if bctl.GLBCBCST in (1, 5):
          obj.GLJHFSYR = fields['GLJHFSYR']
          obj.GLJHFSPR = fields['GLJHFSPR']
          obj.GLJHJEDS = fields['GLJHJEDS']
          obj.GLJHJEDT = fields['GLJHJEDT'].date().tointeger()
          obj.GLJHJERV = fields['GLJHJERV']
          if not session.transaction_started():
            session.begin()
          try:
            session.update(obj)
            session.commit()
          except:
            session.rollback()
            session.expunge(obj)
            raise

      if (mvcsession.execType == MVCExecDelete):
        if not obj:
          raise Exception('Record could not be found')
        if bctl.GLBCBCST not in (1, 4, 5):
          raise Exception('Could not delete journal for this batch %s ' % fields['GLJHBCID'])

        jitms = GLJITM.getObj(True, GLJICONO = cono,
                GLJINOID = glopt['GLOPBCNO'],
                GLJIBCID = int(fields['GLJHBCID']),
                GLJIJEID = int(fields['GLJHJEID']))

        dcm.getcontext().prec = 9
        bctl.GLBCCTTR -= 1
        bctl.GLBCNTDB = dcm.Decimal(bctl.GLBCNTDB, CurrencyContext) - obj.GLJHNTDB
        bctl.GLBCNTCR = dcm.Decimal(bctl.GLBCNTCR, CurrencyContext) - obj.GLJHNTCR
        if not session.transaction_started():
          session.begin()
        try:
          session.update(bctl)
          session.delete(obj)
          session.commit()
        except:
          session.clear()
          session.rollback()
          raise
        for jitm in jitms:
          if not session.transaction_started():
            session.begin()
          try:
            session.delete(jitm)
            session.commit()
          except:
            session.clear()
            session.rollback()
            raise

    return mvcsession















