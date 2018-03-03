"""
G/L Journal Entry Items
"""

__author__    = 'Jaimy Azle'
__version__   = '1.0'
__copyright__ = 'Copyright (c) 2008 Jaimy Azle'

from mvcsvc import *
from elixir import *
import datetime as dt
from validators import *
import decimal as dcm
from ecfutil import CurrencyContext
import sqlalchemy as sa
from tbl import GLJHDR, GLJITM, GLBCTL, GLSOPT, EFUSRS
from tbl import GLACCT, GLSRCE, GLSRCE
from tbl import MSTCUR, MSTXRT, MSTCRT, CURRAT, MSTCMP

class GLS201(MVCController):
  """
  G/L Journal Entry Items
  """
  _description = 'G/L Journal Entry Items'
  _supported_functions = (MVCFuncNew, MVCFuncOpen, MVCFuncShow, MVCFuncDelete)

  GLJIBCID    = MVCField(MVCTypeParam, String(6), label='Batch No.', enabled=False)
  GLJIJEID    = MVCField(MVCTypeParam, String(6), label='Journal. No.', enabled=False)

  GLJIJEDS    = MVCField(MVCTypeParam, String(48), label='Description', enabled=False)
  GLJIJEDT    = MVCField(MVCTypeParam, Date, label='Trans. Date', enabled=False)
  GLJIJERV    = MVCField(MVCTypeParam, Integer(), label='Reversed', enabled=False)
  GLJIJEDB    = MVCField(MVCTypeParam, Numeric(18,4), label='Debit', enabled=False)
  GLJIJECR    = MVCField(MVCTypeParam, Numeric(18,4), label='Credit', enabled=False)

  GLJITRID    = MVCField(MVCTypeList + MVCTypeField, String(6), label='Trans. No.', enabled=False)
  GLJISQNO    = MVCField(MVCTypeList + MVCTypeField, Integer(), label='Seq. No.')
  GLJITRDS    = MVCField(MVCTypeList + MVCTypeField, String(48), label='Description')
  GLJITRRF    = MVCField(MVCTypeField, String(32), label='Reference')
  GLJIACFM    = MVCField(MVCTypeList + MVCTypeField, String(48), label='Acct. ID', browseable=True, synchronized=True)
  GLJIACNM    = MVCField(MVCTypeList + MVCTypeField, String(32), label='Acct. Name', enabled=False)
  GLJITRAM    = MVCField(MVCTypeField, Numeric(18,4), label='Amount', synchronized=True)
  GLJITRTP    = MVCField(MVCTypeField, Integer(), label='Type', synchronized=True, choices = {
                    'Debit':1,
                    'Credit':2})
  GLJITRDB    = MVCField(MVCTypeList, Numeric(18,4), label='Debit')
  GLJITRCR    = MVCField(MVCTypeList, Numeric(18,4), label='Credit')
  GLJISRCL    = MVCField(MVCTypeField, String(5), label='Src Ledger', browseable=True, synchronized=True)
  GLJISRLG    = MVCField(MVCTypeField, String(2), label='Src', enabled=False)
  GLJISRTP    = MVCField(MVCTypeField, String(2), label='Typ', enabled=False)
  GLJITRDT    = MVCField(MVCTypeField, Date, label='Input. Date.')
  GLJICUDC    = MVCField(MVCTypeField, Integer(), label='Dec. Place', enabled=False)
  GLJICHCD    = MVCField(MVCTypeList + MVCTypeField, String(3), label='Currency.', browseable=True, synchronized=True)
  GLJICRTP    = MVCField(MVCTypeField, String(3), label='Rate. Type', browseable=True, synchronized=True)
  GLJICSCD    = MVCField(MVCTypeField, String(3), label='Func. Curr', enabled=False)
  GLJIRTDT    = MVCField(MVCTypeField, Date, label='Rate Date.', browseable=True, synchronized=True)
  GLJIRTOP    = MVCField(MVCTypeField, String(1), label='Rate Operation', enabled=False)
  GLJIDTMT    = MVCField(MVCTypeField, String(1), label='Date Match', enabled=False)
  GLJIRCVL    = MVCField(MVCTypeField, Numeric(15,4), label='Def. Rate', enabled=False)
  GLJIRTVL    = MVCField(MVCTypeField, Numeric(15,4), label='Rate Val')
  GLJIRTSP    = MVCField(MVCTypeField, Numeric(15,4), label='Rate Spread', enabled=False)
  GLJICUAM    = MVCField(MVCTypeField, Numeric(18,4), label='Func. Amount', enabled=False)
  GLJICUDB    = MVCField(MVCTypeList, Numeric(18,4), label='Func. Debit', enabled=False)
  GLJICUCR    = MVCField(MVCTypeList, Numeric(18,4), label='Func. Credit', enabled=False)

  def lookupView(self, session, fieldName):
    ret = MVCLookupDef('','')
    if fieldName == 'GLJIACFM':
      ret.svcname = 'GLS450'
      ret.retfield = 'GLACACFM'
    if fieldName == 'GLJICHCD':
      ret.svcname = 'CMN040'
      ret.retfield = 'CMCRCUCD'
    if fieldName == 'GLJICRTP':
      ret.svcname = 'CMN050'
      ret.retfield = 'CMRTTPCD'
    if fieldName == 'GLJISRCL':
      ret.svcname = 'GLS040'
      ret.retfield = 'GLSRCEID'
    if fieldName == 'GLJIRTDT':
      ret.svcname = 'CMN046'
      ret.params = {'CRRTCUCD':'%f:GLJICSCD', 'CRRTTPCD':'%f:GLJICRTP', 'CRRTSRCP':'%f:GLJICHCD'}
      ret.retfield = 'CRRTRTDT'
    return ret

  def synchronizeData(self, mvcsession, fieldName, fieldType):
    fields = mvcsession.entryDataset.FieldsAsDict()
    params = mvcsession.paramDataset.FieldsAsDict()
    proxy = self.getBusinessObjectProxy()
    usrobj = proxy.getObject('USROBJ')
    glsobj = proxy.getObject('GLSOBJ')
    info = usrobj.retrieveUserInfoDict(mvcsession)
    cono = info['USRCONO']
    glopt = glsobj.getGLOpt(cono)
    if (fieldName == 'GLJISRCL'):
      splitted = GLSRCE.expandSourceCode(fields['GLJISRCL'])
      glsrc = GLSRCE.get(splitted[2])
      if not glsrc:
        raise Exception('G/L Source code is undefined')

      mvcsession.entryDataset.Edit()
      mvcsession.entryDataset.SetFieldValue('GLJISRLG', splitted[0])
      mvcsession.entryDataset.SetFieldValue('GLJISRTP', splitted[1])
      mvcsession.entryDataset.Post()

    if (fieldName == 'GLJIACFM'):
      if (fields['GLJIACFM'] in (None, '')):
        raise Exception('Account ID must not empty')

      acct = GLACCT.stripedacct(fields['GLJIACFM'])
      q = GLACCT.query.filter_by(GLACCONO = cono)
      obj = q.filter_by(GLACACID = acct).first()
      if not obj:
        raise Exception('Account ID does not exist')

      if obj.GLACBLTP == 'D':
        trtp = 1
      else:
        trtp = 2

      mvcsession.entryDataset.Edit()
      mvcsession.entryDataset.SetFieldValue('GLJIACFM', obj.GLACACFM)
      mvcsession.entryDataset.SetFieldValue('GLJIACNM', obj.GLACACNM)
      mvcsession.entryDataset.SetFieldValue('GLJITRTP', trtp)
      mvcsession.entryDataset.Post()

    if (fieldName == 'GLJITRAM'):
      dcm.getcontext().prec = 9
      amount = dcm.Decimal(fields['GLJITRAM'], CurrencyContext)
      if amount < dcm.Decimal(0):
        amount = dcm.Decimal(fields['GLJITRAM'] * dcm.Decimal(-1, CurrencyContext), CurrencyContext)

      mvcsession.entryDataset.Edit()
      mvcsession.entryDataset.SetFieldValue('GLJITRAM', amount)
      mvcsession.entryDataset.Post()

    if (fieldName in ('GLJITRAM', 'GLJICHCD', 'GLJICRTP', 'GLJIRTDT')):

      if (fields['GLJICSCD'] not in (None, '')) and \
         (fields['GLJICRTP'] not in (None, '')):
        crextp = MSTCRT.get((fields['GLJICSCD'], fields['GLJICRTP']))
        if not crextp:
          raise Exception('No exchange rate definition found for combination of currency and rate type used')

        mvcsession.entryDataset.Edit()
        mvcsession.entryDataset.SetFieldValue('GLJIRTOP', crextp.CMCTRTOP)
        mvcsession.entryDataset.SetFieldValue('GLJIDTMT', crextp.CMCTDTMT)
        mvcsession.entryDataset.Post()

      if (fields['GLJICHCD'] not in (None, '')) and \
         (fields['GLJICRTP'] not in (None, '')) and \
         (fields['GLJIRTDT'] not in (None, '')) and \
         (fields['GLJICSCD'] not in (None, '')):

        currat = CURRAT.getRateDate(crextp, fields['GLJICHCD'], \
                    fields['GLJIRTDT'].date().tointeger())
        if not currat:
          raise Exception('Could not find currency rate for selected date')

        mvcsession.entryDataset.Edit()
        mvcsession.entryDataset.SetFieldValue('GLJIRCVL', currat.CRRTRTVL)
        mvcsession.entryDataset.SetFieldValue('GLJIRTVL', currat.CRRTRTVL)
        mvcsession.entryDataset.SetFieldValue('GLJIRTSP', currat.CRRTRTSP)
        mvcsession.entryDataset.Post()

      fields = mvcsession.entryDataset.FieldsAsDict()
      dcm.getcontext().prec = 9
      amount = dcm.Decimal(fields['GLJITRAM'], CurrencyContext)
      if amount < dcm.Decimal(0):
        amount = dcm.Decimal(fields['GLJITRAM'] * dcm.Decimal(-1, CurrencyContext), CurrencyContext)

      namount = dcm.Decimal(0, CurrencyContext)
      if fields['GLJICSCD'] == fields['GLJICHCD']:
        namount = amount
      else:
        if fields['GLJIRTVL']:
          if fields['GLJIRTOP'] == '*':
            namount = amount * dcm.Decimal(fields['GLJIRTVL'])
          elif fields['GLJIRTOP'] == '/':
            divider = dcm.Decimal(fields['GLJIRTVL'])
            if divider <> dcm.Decimal(0):
              namount = amount / divider

      mvcsession.entryDataset.Edit()
      mvcsession.entryDataset.SetFieldValue('GLJICUAM', namount)
      mvcsession.entryDataset.Post()

    return mvcsession

  def openView(self, mvcsession):
    proxy = self.getBusinessObjectProxy()
    usrobj = proxy.getObject('USROBJ')
    glsobj = proxy.getObject('GLSOBJ')
    info = usrobj.retrieveUserInfoDict(mvcsession)
    cono = info['USRCONO']
    glopt = glsobj.getGLOpt(cono)
    if mvcsession.paramDataset.IsEmpty:
      raise Exception('Program GLS201 could not be load directly by user')

    fields = mvcsession.paramDataset.FieldsAsDict()
    if (fields['GLJIBCID'] in (None, '')) or \
       (fields['GLJIJEID'] in (None, '')):
      raise Exception('Program GLS201 could not be open')

    hdr = GLJHDR.getObj(False, GLJHCONO = cono, GLJHNOID = glopt['GLOPBCNO'],
            GLJHBCID = fields['GLJIBCID'], GLJHJEID = fields['GLJIJEID'])
    if not hdr:
      raise Exception('Journal header information could not be retrieved');

    objs = GLJITM.getObj(True, GLJICONO = cono, GLJINOID = glopt['GLOPBCNO'],
            GLJIBCID = fields['GLJIBCID'], GLJIJEID = fields['GLJIJEID'])

    mvcsession.paramDataset.Edit()
    mvcsession.paramDataset.SetFieldValue('GLJIJEDS', hdr.GLJHJEDS)
    mvcsession.paramDataset.SetFieldValue('GLJIJEDT', hdr.GLJHJEDT)
    mvcsession.paramDataset.SetFieldValue('GLJIJERV', hdr.GLJHJERV)
    mvcsession.paramDataset.SetFieldValue('GLJIJEDB', hdr.GLJHNTDB)
    mvcsession.paramDataset.SetFieldValue('GLJIJECR', hdr.GLJHNTCR)
    mvcsession.paramDataset.Post()

    for obj in objs:
      mvcsession.listDataset.CopyFromORM(
        'GLJITRDS;GLJIACFM;GLJIACNM;GLJITRDB;GLJITRCR;GLJICHCD;GLJICUDB;GLJICUCR',
        'GLJITRDS;GLJIACFM;GLJIACNM;GLJITRDB;GLJITRCR;GLJICHCD;GLJICUDB;GLJICUCR',
        obj
      )
      mvcsession.listDataset.Edit()
      mvcsession.listDataset.SetFieldValue('GLJITRID', '%.6d' % obj.GLJITRID)
      mvcsession.listDataset.SetFieldValue('GLJISQNO', obj.GLJISQNO)
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
      params = mvcsession.paramDataset.FieldsAsDict()
      bcid = None
      if params['GLJIBCID'] not in (None, ''):
        obj = GLBCTL.getObj(False, GLBCCONO = cono, GLBCNOID = glopt['GLOPBCNO'], GLBCLSID = params['GLJIBCID'])
        if not obj:
          raise Exception('Batch no %s could not be found')
        # batch status not in (Open, ERROR)
        if obj.GLBCBCST not in (1, 4, 5):
          raise Exception('Could not create a new transaction for this batch %s ' % params['GLJIBCID'])
        bcid = '%.6d' % obj.GLBCLSID

      jhdr = GLJHDR.getObj(False, GLJHCONO = cono,
                GLJHNOID = glopt['GLOPBCNO'],
                GLJHBCID = int(params['GLJIBCID']),
                GLJHJEID = int(params['GLJIJEID']))
      if not jhdr:
        raise Exception('Could not find header transaction')

      fsyr = CSYFSC.validateFiscalYear(glopt['GLOPFSTP'], jhdr.GLJHFSYR, (1,))
      fsprd= CSYFSP.validateFSPeriod2(glopt['GLOPFSTP'], jhdr.GLJHFSYR, jhdr.GLJHFSPR)

      cmpdt = MSTCMP.get(cono)
      crextp = MSTCRT.get((cmpdt.CMCPCUCD, cmpdt.CMCPRTCD))
      if not crextp:
        raise Exception('No exchange rate definition found for combination of '\
          'functional currency and default rate type used in company setting')
      currat = CURRAT.getRateDate(crextp, crextp.CMCTCUCD, dt.date.today().tointeger())

      rtdt = None
      rtvl = None
      rtsp = None
      if currat:
        rtdt = currat.CRRTRTDT
        rtvl = currat.CRRTRTVL
        rtsp = currat.CRRTRTSP

      mvcsession.entryDataset.Append()
      mvcsession.entryDataset.SetFieldValue('GLJITRID', None)
      mvcsession.entryDataset.SetFieldValue('GLJISQNO', 0)
      mvcsession.entryDataset.SetFieldValue('GLJITRDS', None)
      mvcsession.entryDataset.SetFieldValue('GLJITRRF', None)
      mvcsession.entryDataset.SetFieldValue('GLJIACFM', None)
      mvcsession.entryDataset.SetFieldValue('GLJIACNM', None)
      mvcsession.entryDataset.SetFieldValue('GLJITRAM', 0)
      mvcsession.entryDataset.SetFieldValue('GLJITRTP', 1)
      mvcsession.entryDataset.SetFieldValue('GLJISRLG', 'GL')
      mvcsession.entryDataset.SetFieldValue('GLJISRTP', 'JE')
      mvcsession.entryDataset.SetFieldValue('GLJISRCL', 'GL-JE')
      mvcsession.entryDataset.SetFieldValue('GLJITRDT', dt.date.today().tointeger())
      mvcsession.entryDataset.SetFieldValue('GLJICHCD', cmpdt.CMCPCUCD)
      mvcsession.entryDataset.SetFieldValue('GLJICSCD', cmpdt.CMCPCUCD)
      mvcsession.entryDataset.SetFieldValue('GLJICRTP', cmpdt.CMCPRTCD)
      mvcsession.entryDataset.SetFieldValue('GLJIRTOP', crextp.CMCTRTOP)
      mvcsession.entryDataset.SetFieldValue('GLJIDTMT', crextp.CMCTDTMT)
      mvcsession.entryDataset.SetFieldValue('GLJIRTDT', rtdt)
      mvcsession.entryDataset.SetFieldValue('GLJIRCVL', rtvl)
      mvcsession.entryDataset.SetFieldValue('GLJIRTVL', rtvl)
      mvcsession.entryDataset.SetFieldValue('GLJIRTSP', rtsp)
      mvcsession.entryDataset.SetFieldValue('GLJICUAM', 0)
      mvcsession.entryDataset.Post()
    else:
      fields = mvcsession.listDataset.FieldsAsDict()
      params = mvcsession.paramDataset.FieldsAsDict()
      bcid = None
      if params['GLJIBCID'] not in (None, ''):
        obj = GLBCTL.getObj(False, GLBCCONO = cono, GLBCNOID = glopt['GLOPBCNO'], GLBCLSID = params['GLJIBCID'])
        if not obj:
          raise Exception('Batch no %s could not be found')
        # batch status not in (Open, ERROR)
        if mvcsession.execType != MVCExecShow:
          if obj.GLBCBCST not in (1, 4, 5):
            raise Exception('No update/delete permitted on this transaction for batch %s ' % params['GLJIBCID'])
        bcid = '%.6d' % obj.GLBCLSID

      jhdr = GLJHDR.getObj(False, GLJHCONO = cono,
                GLJHNOID = glopt['GLOPBCNO'],
                GLJHBCID = int(params['GLJIBCID']),
                GLJHJEID = int(params['GLJIJEID']))
      if not obj:
        raise Exception('Could not find header transaction')
      obj = GLJITM.getObj(
                False,
                GLJICONO = cono,
                GLJINOID = glopt['GLOPBCNO'],
                GLJIBCID = int(params['GLJIBCID']),
                GLJIJEID = int(params['GLJIJEID']),
                GLJITRID = int(fields['GLJITRID']))
      if not obj:
        raise Exception('Transaction does not exist')

      dcm.getcontext().prec = 9
      amount = dcm.Decimal(obj.GLJITRAM, CurrencyContext)
      namount = dcm.Decimal(obj.GLJICUAM, CurrencyContext)
      if amount < dcm.Decimal(0):
        amount = dcm.Decimal(obj.GLJITRAM * dcm.Decimal(-1, CurrencyContext), CurrencyContext)
        namount = dcm.Decimal(obj.GLJICUAM * dcm.Decimal(-1, CurrencyContext), CurrencyContext)

      mvcsession.entryDataset.Append()
      mvcsession.entryDataset.SetFieldValue('GLJITRID', '%.6d' % obj.GLJITRID)
      mvcsession.entryDataset.SetFieldValue('GLJISQNO', obj.GLJISQNO)
      mvcsession.entryDataset.SetFieldValue('GLJITRDS', obj.GLJITRDS)
      mvcsession.entryDataset.SetFieldValue('GLJITRRF', obj.GLJITRRF)
      mvcsession.entryDataset.SetFieldValue('GLJIACFM', obj.GLJIACFM)
      mvcsession.entryDataset.SetFieldValue('GLJIACNM', obj.GLJIACNM)
      mvcsession.entryDataset.SetFieldValue('GLJITRAM', amount)
      mvcsession.entryDataset.SetFieldValue('GLJITRTP', obj.GLJITRTP)
      mvcsession.entryDataset.SetFieldValue('GLJISRLG', obj.GLJISRLG)
      mvcsession.entryDataset.SetFieldValue('GLJISRTP', obj.GLJISRTP)
      mvcsession.entryDataset.SetFieldValue('GLJISRCL', '%s-%s' % (obj.GLJISRLG, obj.GLJISRTP))
      mvcsession.entryDataset.SetFieldValue('GLJITRDT', obj.GLJITRDT)
      mvcsession.entryDataset.SetFieldValue('GLJICHCD', obj.GLJICHCD)
      mvcsession.entryDataset.SetFieldValue('GLJICSCD', obj.GLJICSCD)
      mvcsession.entryDataset.SetFieldValue('GLJICRTP', obj.GLJICRTP)
      mvcsession.entryDataset.SetFieldValue('GLJIRTOP', obj.GLJIRTOP)
      mvcsession.entryDataset.SetFieldValue('GLJIDTMT', obj.GLJIDTMT)
      mvcsession.entryDataset.SetFieldValue('GLJIRTDT', obj.GLJIRTDT)
      mvcsession.entryDataset.SetFieldValue('GLJIRCVL', obj.GLJIRTVL)
      mvcsession.entryDataset.SetFieldValue('GLJIRTVL', obj.GLJIRTVL)
      mvcsession.entryDataset.SetFieldValue('GLJIRTSP', obj.GLJIRTSP)
      mvcsession.entryDataset.SetFieldValue('GLJICUAM', namount)
      mvcsession.entryDataset.Post()

    return mvcsession

  def postData(self, mvcsession):
    fields = mvcsession.entryDataset.FieldsAsDict()
    params = mvcsession.paramDataset.FieldsAsDict()
    validators.NotEmpty(messages={'empty': 'Acct code must not empty'}).to_python(fields['GLJIACFM'])
    validators.NotEmpty(messages={'empty': 'Nominal amount must not empty'}).to_python(fields['GLJITRAM'])

    proxy = self.getBusinessObjectProxy()
    usrobj = proxy.getObject('USROBJ')
    glsobj = proxy.getObject('GLSOBJ')
    info = usrobj.retrieveUserInfoDict(mvcsession)
    cono = info['USRCONO']
    glopt = glsobj.getGLOpt(cono)

    bcid = None
    if params['GLJIBCID'] not in (None, ''):
      bctl = GLBCTL.getObj(False, GLBCCONO = cono, GLBCNOID = glopt['GLOPBCNO'], GLBCLSID = params['GLJIBCID'])
      if not bctl:
        raise Exception('Batch no %s could not be found')
    else:
      raise Exception('Batch No. could not be retrieved')

    jhdr = GLJHDR.getObj(False, GLJHCONO = cono,
                GLJHNOID = glopt['GLOPBCNO'],
                GLJHBCID = int(params['GLJIBCID']),
                GLJHJEID = int(params['GLJIJEID']))
    if not jhdr:
      raise Exception('Could not find header transaction')

    td = dt.datetime.now()
    if (mvcsession.execType in (MVCExecAppend, MVCExecCopy)):
      if jhdr.GLJHJEST == 2:
        raise Exception('No modification allowed for this kind of journal')
      # batch status not in (Open, ERROR)
      if bctl.GLBCBCST not in (1, 5):
        raise Exception('Could not create a new transaction for this batch %s ' % params['GLJIBCID'])

      lsno = GLJITM.getTRNO(jhdr)
      acct = GLACCT.stripedacct(fields['GLJIACFM'])

      splitted = GLSRCE.expandSourceCode(fields['GLJISRCL'])
      glsrc = GLSRCE.get(splitted[2])
      if not glsrc:
        raise Exception('G/L Source code is undefined')

      rate_date = None
      if fields['GLJICSCD'] != fields['GLJICHCD']:
        validators.NotEmpty(messages={'empty': 'rate date must not empty'}).to_python(fields['GLJIRTDT'])
        crextp = MSTCRT.get((fields['GLJICSCD'], fields['GLJICRTP']))
        if not crextp:
          raise Exception('No exchange rate definition found for combination of currency and rate type used')

        currat = CURRAT.getRateDate(crextp, fields['GLJICHCD'], \
                  fields['GLJIRTDT'].date().tointeger())
        if not currat:
          raise Exception('Could not find currency rate for selected date')

        rate_date = fields['GLJIRTDT'].date().tointeger()

      rec = GLJITM(
          GLJICONO = cono,
          GLJINOID = glopt['GLOPBCNO'],
          GLJIBCID = int(params['GLJIBCID']),
          GLJIJEID = int(params['GLJIJEID']),
          GLJITRID = lsno[0],
          GLJITRDT = fields['GLJITRDT'].date().tointeger(),
          GLJITRDS = fields['GLJITRDS'],
          GLJITRRF = fields['GLJITRRF'],
          GLJISQNO = fields['GLJISQNO'],
          GLJIACID = acct,
          GLJIACFM = fields['GLJIACFM'],
          GLJIACNM = fields['GLJIACNM'],
          GLJITRTP = fields['GLJITRTP'],
          GLJISRLG = fields['GLJISRLG'],
          GLJISRTP = fields['GLJISRTP'],
          GLJICHCD = fields['GLJICHCD'],
          GLJICSCD = fields['GLJICSCD'],
          GLJICRTP = fields['GLJICRTP'],
          GLJIRTOP = fields['GLJIRTOP'],
          GLJIDTMT = fields['GLJIDTMT'],
          GLJIRTDT = rate_date,
          GLJIRCVL = fields['GLJIRCVL'],
          GLJIRTVL = fields['GLJIRTVL'],
          GLJIRTSP = fields['GLJIRTSP'],
          GLJIAUDT = td.date().tointeger(),
          GLJIAUTM = td.time().tointeger(),
          GLJIAUUS = mvcsession.cookies['user_name'].encode('utf8')
        )

      dcm.getcontext().prec = 9
      amount = dcm.Decimal(fields['GLJITRAM'], CurrencyContext)
      if amount < dcm.Decimal(0):
        amount = dcm.Decimal(fields['GLJITRAM'] * dcm.Decimal(-1, CurrencyContext), CurrencyContext)
      amountcr = dcm.Decimal(amount * dcm.Decimal(-1, CurrencyContext), CurrencyContext)

      namount = dcm.Decimal(0, CurrencyContext)
      if fields['GLJICSCD'] == fields['GLJICHCD']:
        namount = amount
      else:
        if fields['GLJIRTVL']:
          deviation = dcm.Decimal(fields['GLJIRTVL'], CurrencyContext) - dcm.Decimal(fields['GLJIRCVL'], CurrencyContext)
          if (abs(deviation) > fields['GLJIRTSP']):
            raise Exception('Currency rate out of it\'s maximum spread allowed')
          if fields['GLJIRTOP'] == '*':
            namount = amount * dcm.Decimal(fields['GLJIRTVL'])
          elif fields['GLJIRTOP'] == '/':
            divider = dcm.Decimal(fields['GLJIRTVL'])
            if divider <> dcm.Decimal(0):
              namount = amount / divider
      namountcr = dcm.Decimal(namount * dcm.Decimal(-1, CurrencyContext), CurrencyContext)

      if rec.GLJITRTP == 1:
        rec.GLJITRDB = amount
        rec.GLJITRAM = amount
        rec.GLJITRCR = dcm.Decimal(0, CurrencyContext)
        rec.GLJICUAM = namount
        rec.GLJICUDB = namount
        rec.GLJICUCR = dcm.Decimal(0, CurrencyContext)
      else:
        rec.GLJITRCR = amount
        rec.GLJITRAM = amountcr
        rec.GLJITRDB = dcm.Decimal(0, CurrencyContext)
        rec.GLJICUAM = namountcr
        rec.GLJICUCR = namount
        rec.GLJICUDB = dcm.Decimal(0, CurrencyContext)

      bctl.GLBCNTDB = dcm.Decimal(bctl.GLBCNTDB, CurrencyContext) - jhdr.GLJHNTDB
      bctl.GLBCNTCR = dcm.Decimal(bctl.GLBCNTCR, CurrencyContext) - jhdr.GLJHNTCR

      jhdr.GLJHNTDB = dcm.Decimal(jhdr.GLJHNTDB, CurrencyContext) + rec.GLJITRDB
      jhdr.GLJHNTCR = dcm.Decimal(jhdr.GLJHNTCR, CurrencyContext) + rec.GLJITRCR

      bctl.GLBCNTDB = dcm.Decimal(bctl.GLBCNTDB, CurrencyContext) + jhdr.GLJHNTDB
      bctl.GLBCNTCR = dcm.Decimal(bctl.GLBCNTCR, CurrencyContext) + jhdr.GLJHNTCR

      if not session.transaction_started():
        session.begin()
      try:
        session.save(rec)
        session.update(jhdr)
        session.update(bctl)
        session.commit()
      except:
        session.clear()
        session.rollback()
        raise

    if (mvcsession.execType in (MVCExecEdit, MVCExecDelete)):
      # batch status not in (Open, ERROR)
      if bctl.GLBCBCST not in (1, 4, 5):
        raise Exception('Could not change transaction on this batch %s ' % params['GLJIBCID'])

      jitm = GLJITM.getObj(False, GLJICONO = cono,
                GLJINOID = glopt['GLOPBCNO'],
                GLJIBCID = int(params['GLJIBCID']),
                GLJIJEID = int(params['GLJIJEID']),
                GLJITRID = fields['GLJITRID'])
      if not jitm:
        raise Exception('Transaction could not be find on the database')

      if (mvcsession.execType == MVCExecEdit):
        if jhdr.GLJHJEST == 2:
          raise Exception('No modification allowed for this kind of journal')
        rate_date = None
        if fields['GLJICSCD'] != fields['GLJICHCD']:
          crextp = MSTCRT.get((fields['GLJICSCD'], fields['GLJICRTP']))
          if not crextp:
            raise Exception('No exchange rate definition found for combination of currency and rate type used')

          currat = CURRAT.getRateDate(crextp, fields['GLJICHCD'], \
                    fields['GLJIRTDT'].date().tointeger())
          if not currat:
            raise Exception('Could not find currency rate for selected date')

          rate_date = fields['GLJIRTDT'].date().tointeger()

        splitted = GLSRCE.expandSourceCode(fields['GLJISRCL'])
        glsrc = GLSRCE.get(splitted[2])
        if not glsrc:
          raise Exception('G/L Source code is undefined')

        dcm.getcontext().prec = 9
        amount = dcm.Decimal(fields['GLJITRAM'], CurrencyContext)
        if amount < dcm.Decimal(0):
          amount = dcm.Decimal(amount * dcm.Decimal(-1, CurrencyContext), CurrencyContext)
        amountcr = dcm.Decimal(amount * dcm.Decimal(-1, CurrencyContext), CurrencyContext)

        namount = dcm.Decimal(0, CurrencyContext)
        if fields['GLJICSCD'] == fields['GLJICHCD']:
          namount = amount
        else:
          if fields['GLJIRTVL']:
            deviation = dcm.Decimal(fields['GLJIRTVL'], CurrencyContext) - dcm.Decimal(fields['GLJIRCVL'], CurrencyContext)
            if (abs(deviation) > fields['GLJIRTSP']):
              raise Exception('Currency rate out of it\'s maximum spread allowed')
            if fields['GLJIRTOP'] == '*':
              namount = amount * dcm.Decimal(fields['GLJIRTVL'])
            elif fields['GLJIRTOP'] == '/':
              divider = dcm.Decimal(fields['GLJIRTVL'])
              if divider <> dcm.Decimal(0):
                namount = amount / divider
        namountcr = dcm.Decimal(namount * dcm.Decimal(-1, CurrencyContext), CurrencyContext)

        bctl.GLBCNTDB = dcm.Decimal(bctl.GLBCNTDB, CurrencyContext) - jhdr.GLJHNTDB
        bctl.GLBCNTCR = dcm.Decimal(bctl.GLBCNTCR, CurrencyContext) - jhdr.GLJHNTCR

        jhdr.GLJHNTDB = dcm.Decimal(jhdr.GLJHNTDB, CurrencyContext) - jitm.GLJITRDB
        jhdr.GLJHNTCR = dcm.Decimal(jhdr.GLJHNTCR, CurrencyContext) - jitm.GLJITRCR

        if fields['GLJITRTP'] == 1:
          jitm.GLJITRDB = amount
          jitm.GLJITRAM = amount
          jitm.GLJITRCR = dcm.Decimal(0, CurrencyContext)
          jitm.GLJICUDB = namount
          jitm.GLJICUAM = namount
          jitm.GLJICUCR = dcm.Decimal(0, CurrencyContext)
        else:
          jitm.GLJITRCR = amount
          jitm.GLJITRAM = amountcr
          jitm.GLJITRDB = dcm.Decimal(0, CurrencyContext)
          jitm.GLJICUCR = namount
          jitm.GLJICUAM = namountcr
          jitm.GLJICUDB = dcm.Decimal(0, CurrencyContext)

        jhdr.GLJHNTDB = dcm.Decimal(jhdr.GLJHNTDB, CurrencyContext) + jitm.GLJITRDB
        jhdr.GLJHNTCR = dcm.Decimal(jhdr.GLJHNTCR, CurrencyContext) + jitm.GLJITRCR

        bctl.GLBCNTDB = dcm.Decimal(bctl.GLBCNTDB, CurrencyContext) + jhdr.GLJHNTDB
        bctl.GLBCNTCR = dcm.Decimal(bctl.GLBCNTCR, CurrencyContext) + jhdr.GLJHNTCR

        acct = GLACCT.stripedacct(fields['GLJIACFM'])
        jitm.GLJITRDS = fields['GLJITRDS']
        jitm.GLJITRRF = fields['GLJITRRF']
        jitm.GLJISQNO = fields['GLJISQNO']
        jitm.GLJIACID = acct
        jitm.GLJIACFM = fields['GLJIACFM']
        jitm.GLJIACNM = fields['GLJIACNM']
        jitm.GLJISRLG = fields['GLJISRLG']
        jitm.GLJISRTP = fields['GLJISRTP']
        jitm.GLJITRTP = fields['GLJITRTP']
        jitm.GLJISRLG = fields['GLJISRLG']
        jitm.GLJISRTP = fields['GLJISRTP']
        jitm.GLJITRDT = fields['GLJITRDT'].date().tointeger()
        jitm.GLJICHCD = fields['GLJICHCD']
        jitm.GLJICSCD = fields['GLJICSCD']
        jitm.GLJICRTP = fields['GLJICRTP']
        jitm.GLJIRTOP = fields['GLJIRTOP']
        jitm.GLJIDTMT = fields['GLJIDTMT']
        jitm.GLJIRTDT = rate_date
        jitm.GLJIRTVL = fields['GLJIRTVL']
        jitm.GLJIRTSP = fields['GLJIRTSP']
        jitm.GLJIAUDT = td.date().tointeger()
        jitm.GLJIAUTM = td.time().tointeger()
        jitm.GLJIAUUS = mvcsession.cookies['user_name'].encode('utf8')

        if not session.transaction_started():
          session.begin()
        try:
          session.update(jitm)
          session.update(jhdr)
          session.update(bctl)
          session.commit()
        except:
          session.clear()
          session.rollback()
          raise

      if (mvcsession.execType == MVCExecDelete):
        dcm.getcontext().prec = 9
        bctl.GLBCNTDB = dcm.Decimal(bctl.GLBCNTDB, CurrencyContext) - jhdr.GLJHNTDB
        bctl.GLBCNTCR = dcm.Decimal(bctl.GLBCNTCR, CurrencyContext) - jhdr.GLJHNTCR

        jhdr.GLJHNTDB = dcm.Decimal(jhdr.GLJHNTDB, CurrencyContext) - jitm.GLJITRDB
        jhdr.GLJHNTCR = dcm.Decimal(jhdr.GLJHNTCR, CurrencyContext) - jitm.GLJITRCR

        bctl.GLBCNTDB = dcm.Decimal(bctl.GLBCNTDB, CurrencyContext) + jhdr.GLJHNTDB
        bctl.GLBCNTCR = dcm.Decimal(bctl.GLBCNTCR, CurrencyContext) + jhdr.GLJHNTCR

        if not session.transaction_started():
          session.begin()
        try:
          session.delete(jitm)
          session.update(jhdr)
          session.update(bctl)
          session.commit()
        except:
          session.clear()
          session.rollback()
          raise
    return mvcsession

