"""
G/L Book Of Account
"""
__author__    = 'Jaimy Azle'
__version__   = '1.0'
__copyright__ = 'Copyright (c) 2008 Jaimy Azle'

from mvcsvc import *
from elixir import *
import datetime as dt
from validators import *
import sqlalchemy as sa
import re
from tbl import GLACCT, EFUSRS, GLSACS, GLSOPT, MSTUOM, GLSRCE, MSTCMP

class GLS450(MVCController):
  """
  G/L Book Of Account
  """
  _description = 'G/L Book Of Account'
  _supported_functions = (MVCFuncNew, MVCFuncOpen, MVCFuncShow, MVCFuncCopy, MVCFuncDelete)


  GLPRCONO    = MVCField(MVCTypeParam, String(3), label='Comp. ID', visible=False)
  GLPRACST    = MVCField(MVCTypeParam, Integer(), label='Status',
                  choices={
                      'Disable':0,
                      'Enable':1
                  })
  GLPRGRTP    = MVCField(MVCTypeParam, Integer(), label='Acct. group',
                  choices={
                        'All groups':0,
                        'Current assets':1,
                        'Fixed assets':2,
                        'Other assets':3,
                        'Accumulated depreciation':4,
                        'Current liabilities':5,
                        'Long term liabilities':6,
                        'Stockholders\' equity':7,
                        'Revenue':8,
                        'Cost of sales':9,
                        'Opening inventory':10,
                        'Purchases':11,
                        'Closing inventory':12,
                        'Cost and expenses':13,
                        'Other income and expenses':14,
                        'Provision for income taxes':15,
                        'Others':17
                  })
  GLACACFM    = MVCField(MVCTypeList + MVCTypeField, String(48), label='Account', charcase=ecUpperCase, synchronized=True)
  GLACACNM    = MVCField(MVCTypeList + MVCTypeField, String(32), label='Description')
  GLACACID    = MVCField(MVCTypeList, String(48), label='Account ID', visible = False)
  GLACACTP    = MVCField(MVCTypeField, String(1), label='Acct. Type',
                  choices={
                      'Income Statement':'I',
                      'Balance Sheet':'B',
                      'Retained Earnings':'R'
                  })
  GLACTPNM    = MVCField(MVCTypeList, String(16), label='Type',
                  choices={
                        'I':'Income Statement',
                        'B':'Balance Sheet',
                        'R':'Retained Earnings'
                  })
  GLACBLTP    = MVCField(MVCTypeField, String(1), label='Normal balance',
                  choices={
                        'Debit':'D',
                        'Credit':'C'
                  })
  GLACBLNM    = MVCField(MVCTypeList, String(8), label='Balance',
                  choices={
                        'D':'Debit',
                        'C':'Credit'
                  })
  GLACGRTP    = MVCField(MVCTypeField, Integer(), label='Acct. group',
                  choices={
                        'Current assets':1,
                        'Fixed assets':2,
                        'Other assets':3,
                        'Accumulated depreciation':4,
                        'Current liabilities':5,
                        'Long term liabilities':6,
                        'Stockholders\' equity':7,
                        'Revenue':8,
                        'Cost of sales':9,
                        'Opening inventory':10,
                        'Purchases':11,
                        'Closing inventory':12,
                        'Cost and expenses':13,
                        'Other income and expenses':14,
                        'Provision for income taxes':15,
                        'Others':17
                  })
  GLACGRNM    = MVCField(MVCTypeList, String(32), label='Group',
                  choices={
                        1:'Current assets',
                        2:'Fixed assets',
                        3:'Other assets',
                        4:'Accumulated depreciation',
                        5:'Current liabilities',
                        6:'Long term liabilities',
                        7:'Stockholders\' equity',
                        8:'Revenue',
                        9:'Cost of sales',
                        10:'Opening inventory',
                        11:'Purchases',
                        12:'Closing inventory',
                        13:'Cost and expenses',
                        14:'Other income and expenses',
                        15:'Provision for income taxes',
                        16:'Others'
                  })
  GLACACST    = MVCField(MVCTypeField, Integer(), label='Acct. Enabled')
  GLACATNM    = MVCField(MVCTypeList, String(8), label='Acct. Enabled',
                  choices={
                        0:'Disabled',
                        1:'Enabled'
                  })
  GLACCSST    = MVCField(MVCTypeField, Integer(), label='Posting to acct',
                  choices={
                        'Detail':0,
                        'Consolidated':1
                  })
  GLACALST    = MVCField(MVCTypeField, Integer(), label='Auto allocation', synchronized=True)
  GLACALSR    = MVCField(MVCTypeField, String(5), label='Allocation source code', synchronized=True, browseable=True)
  GLACSRNM    = MVCField(MVCTypeField, String(48),label='Source code name', enabled=False)
  GLACSTID    = MVCField(MVCTypeField, String(8), label='Default structure', synchronized=True, browseable=True)
  GLACSTNM    = MVCField(MVCTypeField, String(32),label='structure name', enabled=False)
  GLACCUCD    = MVCField(MVCTypeField, String(3), label='Default Currency', browseable=True)
  GLACCPTP    = MVCField(MVCTypeField, Integer(), label='Post in',
                  choices ={
                        'All Currencies':1,
                        'Specified Currencies':2
                  })

  def initView(self, mvcsession):
    mvcsession.extFunctions = ( MVCExtFunction('G/L Allocation Items', 'GLS451', params = {'GLALACID':'%f:GLACACID','GLALACFM':'%f:GLACACFM', 'GLALACNM':'%f:GLACACNM'}),
                                MVCExtFunction('G/L Account Currencies', 'GLS452', params = {'GLRVACID':'%f:GLACACID','GLRVACFM':'%f:GLACACFM', 'GLRVACNM':'%f:GLACACNM'}))
    return mvcsession

  def lookupView(self, session, fieldName):
    ret = MVCLookupDef('','')
    if fieldName == 'GLACALSR':
      ret.svcname = 'GLS040'
      ret.retfield = 'GLSRCEID'
    if fieldName == 'GLACSTID':
      ret.svcname = 'GLS030'
      ret.retfield = 'ACASACCD'
    if fieldName == 'GLACCUCD':
      ret.svcname = 'CMN040'
      ret.retfield = 'CMCRCUCD'
    return ret

  def synchronizeData(self, mvcsession, fieldName, fieldType):
    fields = mvcsession.entryDataset.FieldsAsDict()
    proxy = self.getBusinessObjectProxy()
    usrobj = proxy.getObject('USROBJ')
    glsobj = proxy.getObject('GLSOBJ')
    info = usrobj.retrieveUserInfoDict(mvcsession)
    cono = info['USRCONO']
    glopt = glsobj.getGLOpt(cono)

    if (fieldName == 'GLACALSR') and \
       (fields['GLACALSR'] not in (None, '')):

      srcid = GLSRCE.expandSourceCode(fields['GLACALSR'])
      obj = GLSRCE.query.filter_by(GLSRCEID = srcid[2]).first()
      if not obj:
        raise Exception('U/M code %s is not valid' % fields['GLACALSR'])

      mvcsession.entryDataset.Edit()
      mvcsession.entryDataset.SetFieldValue('GLACSRNM', obj.GLSRCENM)
      mvcsession.entryDataset.Post()

    if (fieldName == 'GLACSTID') and \
       (fields['GLACSTID'] not in (None, '')):
      obj = GLSACS.query.filter_by(ACASACCD = fields['GLACSTID']).first()
      if not obj:
        raise Exception('Account structure %s is not valid' % fields['GLACSTID'])

      mvcsession.entryDataset.Edit()
      mvcsession.entryDataset.SetFieldValue('GLACSTNM', obj.ACASACNM)
      mvcsession.entryDataset.Post()

    if ((fieldName == 'GLACSTID') or (fieldName == 'GLACACFM')) and \
       (fields['GLACACFM'] not in (None, '')) and \
       (fields['GLACSTID'] not in (None, '')) and \
       (cono != None):

      fmtvalue = glsobj.formatacct(cono, fields['GLACSTID'], fields['GLACACFM'])
      mvcsession.entryDataset.Edit()
      mvcsession.entryDataset.SetFieldValue('GLACACFM', fmtvalue[0])
      mvcsession.entryDataset.Post()

    # if (fieldName == 'GLACALST'):
    #   mvcsession.fieldDefs.GLACALSR.enabled = fields['GLACALST'] == 1
    return mvcsession

  def openView(self, mvcsession):
    proxy = self.getBusinessObjectProxy()
    usrobj = proxy.getObject('USROBJ')
    glsobj = proxy.getObject('GLSOBJ')
    info = usrobj.retrieveUserInfoDict(mvcsession)
    cono = info['USRCONO']
    glopt = glsobj.getGLOpt(cono)
    if mvcsession.paramDataset.RecordCount == 0:
      if cono is None:
        cono = ''
      mvcsession.paramDataset.Append()
      mvcsession.paramDataset.SetFieldValue('GLPRCONO', cono)
      mvcsession.paramDataset.SetFieldValue('GLPRACST', 1)
      mvcsession.paramDataset.SetFieldValue('GLPRGRTP', 0)
      mvcsession.paramDataset.Post()

    params = mvcsession.paramDataset.FieldsAsDict()
    q = GLACCT.query
    q = q.filter_by(GLACCONO =  params['GLPRCONO'])
    q = q.filter_by(GLACACST = params['GLPRACST'])
    if params['GLPRGRTP'] != 0:
      q = q.filter_by(GLACGRTP = params['GLPRGRTP'])
    q = q.order_by(sa.asc(GLACCT.GLACACID))
    objs = q.all()

    for obj in objs:
      mvcsession.listDataset.Append()
      mvcsession.listDataset.SetFieldValue('GLACACID', obj.GLACACID)
      mvcsession.listDataset.SetFieldValue('GLACACFM', obj.GLACACFM)
      mvcsession.listDataset.SetFieldValue('GLACACNM', obj.GLACACNM)
      if obj.GLACACTP != None:
        mvcsession.listDataset.SetFieldValue('GLACTPNM', mvcsession.fieldDefs.GLACTPNM.choices[obj.GLACACTP])
      if obj.GLACBLTP != None:
        mvcsession.listDataset.SetFieldValue('GLACBLNM', mvcsession.fieldDefs.GLACBLNM.choices[obj.GLACBLTP])
      if obj.GLACGRTP != None:
        mvcsession.listDataset.SetFieldValue('GLACGRNM', mvcsession.fieldDefs.GLACGRNM.choices[obj.GLACGRTP])
      if obj.GLACACST != None:
        mvcsession.listDataset.SetFieldValue('GLACATNM', mvcsession.fieldDefs.GLACATNM.choices[obj.GLACACST])
      mvcsession.listDataset.Post()
    return mvcsession

  def retrieveData(self, mvcsession):
    listFields = mvcsession.listDataset.FieldsAsDict()
    paramFields = mvcsession.paramDataset.FieldsAsDict()
    proxy = self.getBusinessObjectProxy()
    usrobj = proxy.getObject('USROBJ')
    glsobj = proxy.getObject('GLSOBJ')
    info = usrobj.retrieveUserInfoDict(mvcsession)
    cono = info['USRCONO']
    glopt = glsobj.getGLOpt(cono)
    if (cono in (None, '')):
      raise Exception('Default company for user % is not assigned' % mvcsession.cookies['user_name'].encode('utf8'))

    if mvcsession.execType == MVCExecAppend:
      opt = GLSOPT.query.filter_by(GLOPCONO = cono).first()
      mstcmp = MSTCMP.get(cono)
      if not mstcmp:
        raise Exception('Default company has not been setup')
      if not opt:
        raise Exception('G/L option has not been setup')
      # set default field value
      mvcsession.entryDataset.Append()
      mvcsession.entryDataset.SetFieldValue('GLACSTID', opt.GLOPACSC)
      mvcsession.entryDataset.SetFieldValue('GLACACTP', 'I')
      mvcsession.entryDataset.SetFieldValue('GLACBLTP', 'D')
      mvcsession.entryDataset.SetFieldValue('GLACGRTP', 1)
      mvcsession.entryDataset.SetFieldValue('GLACACST', 1)
      mvcsession.entryDataset.SetFieldValue('GLACCSST', 0)
      mvcsession.entryDataset.SetFieldValue('GLACALST', 0)
      mvcsession.entryDataset.SetFieldValue('GLACCUCD', mstcmp.CMCPCUCD)
      mvcsession.entryDataset.SetFieldValue('GLACCPTP', 1)
      if (opt.GLOPACSC not in (None, '')):
        obj = GLSACS.query.filter_by(ACASACCD = opt.GLOPACSC).first()
        if not obj:
          raise Exception('Account structure %s is not found' % fields['GLACSTID'])
        mvcsession.entryDataset.SetFieldValue('GLACSTNM', obj.ACASACNM)
      mvcsession.entryDataset.Post()

    if mvcsession.execType in (MVCExecShow, MVCExecEdit, MVCExecDelete, MVCExecCopy):
      pre = re.compile('\w+')
      q = GLACCT.query
      q = q.filter_by(GLACCONO = cono)
      q = q.filter_by(GLACACID = ''.join(pre.findall(listFields['GLACACFM'])))
      obj = q.first()

      if (mvcsession.execType != MVCExecCopy):
        mvcsession.entryDataset.CopyFromORM(
          'GLACACFM;GLACACNM;GLACACTP;GLACBLTP;GLACGRTP;'\
          'GLACACST;GLACCSST;GLACALST;GLACALSR;GLACSRNM;GLACSTID;GLACSTNM;GLACCUCD;GLACCPTP',
          'GLACACFM;GLACACNM;GLACACTP;GLACBLTP;GLACGRTP;'\
          'GLACACST;GLACCSST;GLACALST;GLACALSR;GLACSRNM;GLACSTID;GLACSTNM;GLACCUCD;GLACCPTP',
          obj)
      else:
        mvcsession.entryDataset.CopyFromORM(
          'GLACACTP;GLACBLTP;GLACGRTP;'\
          'GLACACST;GLACCSST;GLACALST;GLACALSR;GLACSRNM;GLACSTID;GLACSTNM',
          'GLACACTP;GLACBLTP;GLACGRTP;'\
          'GLACACST;GLACCSST;GLACALST;GLACALSR;GLACSRNM;GLACSTID;GLACSTNM',
          obj)

      if obj.GLACALSR is not (None, ''):
        srcid = obj.GLACALSR
        if srcid not in (None, ''):
          mvcsession.entryDataset.Edit()
          mvcsession.entryDataset.SetFieldValue('GLACALSR', "%s-%s" % (srcid[:2], srcid[2:]))
          mvcsession.entryDataset.Post()

    if mvcsession.execType == MVCExecEdit:
      mvcsession.fieldDefs.GLACACFM.enabled = False
      mvcsession.fieldDefs.GLACSTID.enabled = False

    # fields = mvcsession.entryDataset.FieldsAsDict()
    # mvcsession.fieldDefs.GLACALSR.enabled = fields['GLACALST'] == 1
    return mvcsession

  def postData(self, mvcsession):
    fields = mvcsession.entryDataset.FieldsAsDict()
    validators.NotEmpty(messages={'empty': 'Acct code must not empty'}).to_python(fields['GLACACFM'])
    validators.NotEmpty(messages={'empty': 'Default acct structure must not empty'}).to_python(fields['GLACSTID'])
    proxy = self.getBusinessObjectProxy()
    usrobj = proxy.getObject('USROBJ')
    glsobj = proxy.getObject('GLSOBJ')
    info = usrobj.retrieveUserInfoDict(mvcsession)
    cono = info['USRCONO']
    glopt = glsobj.getGLOpt(cono)
    if (cono in (None, '')):
      raise Exception('Default company for user % is not assigned' % mvcsession.cookies['user_name'].encode('utf8'))
    pre = re.compile('\w+')
    acct = ''.join(pre.findall(fields['GLACACFM']))
    acctvalues = glsobj.formatacct(cono, fields['GLACSTID'], acct)
    q = GLACCT.query
    q = q.filter_by(GLACCONO = cono)
    q = q.filter_by(GLACACID = acct)
    obj = q.first()
    td = dt.datetime.now()
    srcid = None
    if fields['GLACALSR'] not in (None, ''):
      srcid = GLSRCE.expandSourceCode(fields['GLACALSR'])[2]
    if (mvcsession.execType in (MVCExecAppend, MVCExecCopy)):
      if obj:
        raise Exception('Duplicate record found')
      rec = GLACCT(
        GLACCONO = cono,
        GLACACID = acct,
        GLACACFM = acctvalues[0],
        GLACACNM = fields['GLACACNM'],
        GLACACTP = fields['GLACACTP'],
        GLACBLTP = fields['GLACBLTP'],
        GLACGRTP = fields['GLACGRTP'],
        GLACACST = fields['GLACACST'],
        GLACCSST = fields['GLACCSST'],
        GLACALST = fields['GLACALST'],
        GLACALSR = srcid,
        GLACSRNM = fields['GLACSRNM'],
        GLACALTO = 0,
        GLACALPC = 0,
        GLACSTID = fields['GLACSTID'],
        GLACSTNM = fields['GLACSTNM'],
        GLACLCST = 0,
        GLACCUCD = fields['GLACCUCD'],
        GLACCPTP = fields['GLACCPTP'],
        GLACAUDT = td.date().tointeger(),
        GLACAUTM = td.time().tointeger(),
        GLACAUUS = mvcsession.cookies['user_name'].encode('utf8')
      )
      for (csid, csvalue) in acctvalues[1:]:
        setattr(rec, 'GLACCS%.2d' % csid, csvalue)

      if not session.transaction_started():
        session.begin()
      try:
        session.save(rec)
        session.commit()
      except:
        session.rollback()
        session.expunge(rec)
        raise
    if (mvcsession.execType == MVCExecEdit):
      if not obj:
        raise Exception('Record could not be found')
      mvcsession.entryDataset.CopyIntoORM(
        'GLACACFM;GLACACNM;GLACACTP;GLACBLTP;GLACGRTP;'\
        'GLACACST;GLACCSST;GLACALST;GLACALSR;GLACSRNM;GLACSTID;GLACSTNM;GLACCUCD;GLACCPTP',
        'GLACACFM;GLACACNM;GLACACTP;GLACBLTP;GLACGRTP;'\
        'GLACACST;GLACCSST;GLACALST;GLACALSR;GLACSRNM;GLACSTID;GLACSTNM;GLACCUCD;GLACCPTP',
        obj)
      obj.GLACALSR = srcid
      obj.GLACAUDT = td.date().tointeger()
      obj.GLACAUTM = td.time().tointeger()
      obj.GLACAUUS = mvcsession.cookies['user_name'].encode('utf8')
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
      if not session.transaction_started():
        session.begin()
      try:
        session.delete(obj)
        session.commit()
      except:
        session.rollback()
        raise
    return mvcsession

