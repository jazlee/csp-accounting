"""
UoM Conversion Table, this module purposed for maintaining UoM Conversion Table
which will be required by various modules on this system.
"""
__author__    = 'Jaimy Azle'
__version__   = '1.0'
__copyright__ = 'Copyright (c) 2008 Jaimy Azle'

from mvcsvc import *
from elixir import *
import datetime as dt
import sqlalchemy as sa
from validators import *
from tbl import UOMCVT, MSTUOM

class CMN065(MVCController):
  """
  UoM Conversion Table, this module purposed for maintaining UoM Conversion Table
  which will be required by various modules on this system.
  """

  _description = 'UoM Conversion Table'
  _supported_functions = (MVCFuncNew, MVCFuncOpen, MVCFuncShow,
    MVCFuncCopy, MVCFuncDelete)
  _model_binder = MVCModelBinder(UOMCVT)

  CVUMCONO  = MVCField(MVCTypeList + MVCTypeField + MVCTypeParam, String(3),
                label='Comp.ID',
                enabled=False,
                visible=False)
  CVUMUMCD  = MVCField(MVCTypeList + MVCTypeField + MVCTypeParam, String(3),
                label='Basic U/M',
                charcase=ecUpperCase,
                browseable=True,
                synchronized=True)
  CVUMUMNM  = MVCField(MVCTypeList + MVCTypeField, String(16),
                label='Basic U/M Name',
                enabled=False)
  CVUMALCD  = MVCField(MVCTypeList + MVCTypeField + MVCTypeParam, String(3),
                label='Alt. U/M',
                charcase=ecUpperCase,
                browseable=True,
                synchronized=True)
  CVUMALNM  = MVCField(MVCTypeList + MVCTypeField, String(16),
                label='Alt. U/M Name',
                enabled=False)
  CVUMCVFA  = MVCField(MVCTypeList + MVCTypeField, Numeric(15, 4),
                label='Conv. Factor')
  CVUMCVFR  = MVCField(MVCTypeList + MVCTypeField, String(1),
                label='Conv. Method',
                choices={'* - Multiplication':'*', '/ - Division':'/'})
  CVUMCVRV  = MVCField(MVCTypeField, Integer(),
                label='Auto create reverse conversion')

  def lookupView(self, session, fieldName):
    ret = MVCLookupDef('','')
    if fieldName in ('CVUMUMCD','CVUMALCD'):
      ret.svcname = 'CMN060'
      ret.retfield = 'CMUMUMCD'
    return ret

  def synchronizeData(self, mvcsession, fieldName, fieldType):
    fields = mvcsession.entryDataset.FieldsAsDict()
    proxy = self.getBusinessObjectProxy()
    uomobj = proxy.getObject('UOMOBJ')
    if fieldName == 'CVUMUMCD':
      uminfo = uomobj.getUMCode(fields['CVUMCONO'], fields['CVUMUMCD'])
      mvcsession.entryDataset.Edit()
      mvcsession.entryDataset.SetFieldValue('CVUMUMCD', uminfo[0])
      mvcsession.entryDataset.SetFieldValue('CVUMUMNM', uminfo[1])
      mvcsession.entryDataset.Post()
    elif fieldName == 'CVUMALCD':
      uminfo = uomobj.getUMCode(fields['CVUMCONO'], fields['CVUMALCD'])
      mvcsession.entryDataset.Edit()
      mvcsession.entryDataset.SetFieldValue('CVUMALCD', uminfo[0])
      mvcsession.entryDataset.SetFieldValue('CVUMALNM', uminfo[1])
      mvcsession.entryDataset.Post()
    return mvcsession

  def initializeParam(self, mvcsession, query):
    '''Initialize parameters'''
    params = mvcsession.paramDataset.FieldsAsDict()
    proxy = self.getBusinessObjectProxy()
    if params['CVUMCONO'] in (None, ''):
      usrobj = proxy.getObject('USROBJ')
      infodict = usrobj.retrieveUserInfoDict(mvcsession)
      params['CVUMCONO'] = infodict['USRCONO']

      mvcsession.paramDataset.Edit()
      mvcsession.paramDataset.SetFieldValue('CVUMCONO', params['CVUMCONO'])
      mvcsession.paramDataset.Post()

    cmpobj = proxy.getObject('CMPOBJ')
    cmpobj.validateCompany(params['CVUMCONO'])

    query = query.filter_by( CVUMCONO = params['CVUMCONO'])
    if (params['CVUMUMCD'] != None) and (params['CVUMUMCD'] != ''):
      query = query.filter_by(CVUMUMCD = params['CVUMUMCD'])
    if (params['CVUMALCD'] != None) and (params['CVUMALCD'] != ''):
      query = query.filter_by(CVUMALCD = params['CVUMALCD'])
    query = query.order_by(sa.asc(UOMCVT.CVUMUMCD))
    return query

  def initializeData(self, mvcsession):
    '''Initializing data'''
    params = mvcsession.paramDataset.FieldsAsDict()
    mvcsession.entryDataset.Append()
    mvcsession.entryDataset.SetFieldValues(params)
    mvcsession.entryDataset.SetFieldValue('CVUMCVFR', '*')
    mvcsession.entryDataset.SetFieldValue('CVUMCVRV', 1)
    mvcsession.entryDataset.SetFieldValue('CVUMCVFA', 1)
    mvcsession.entryDataset.Post()
    self.synchronizeData(mvcsession, 'CVUMUMCD', MVCTypeField)
    self.synchronizeData(mvcsession, 'CVUMALCD', MVCTypeField)
    return mvcsession

  def afterRetrieveData(self, mvcsession, obj):
    '''Event triggered after retrieving data'''
    mvcsession.fieldDefs.CVUMCVRV.enabled = False
    return (mvcsession, obj)

  def ensureUM(self, umname):
    obj = MSTUOM.query.filter_by(CMUMUMCD = umname).first()
    if not obj:
      raise Exception('U/M "%s" does not found' % umname)

  def postData(self, mvcsession):
    fields = mvcsession.entryDataset.FieldsAsDict()
    if (fields['CVUMUMCD'] == '') or (fields['CVUMUMCD'] is None) or \
       (fields['CVUMALCD'] == '') or (fields['CVUMALCD'] is None):
      raise Exception('Basic and Alternate U/M must be specified')
    self.ensureUM(fields['CVUMUMCD'])
    self.ensureUM(fields['CVUMALCD'])
    q = UOMCVT.query
    q = q.filter_by(CVUMUMCD = fields['CVUMUMCD'])
    q = q.filter_by(CVUMALCD = fields['CVUMALCD'])
    obj = q.first()
    td = dt.datetime.now()
    if (mvcsession.execType in (MVCExecAppend, MVCExecCopy)):
      if obj:
        raise Exception('Duplicate record found')
      validators.NotEmpty(messages={'empty': 'basic U/M code must not empty'}).to_python(fields['CVUMUMCD'])
      validators.NotEmpty(messages={'empty': 'alternate U/M code must not empty'}).to_python(fields['CVUMALCD'])
      rec1 = UOMCVT(
        CVUMCONO = fields['CVUMCONO'],
        CVUMUMCD = fields['CVUMUMCD'],
        CVUMUMNM = fields['CVUMUMNM'],
        CVUMALCD = fields['CVUMALCD'],
        CVUMALNM = fields['CVUMALNM'],
        CVUMCVFA = fields['CVUMCVFA'],
        CVUMCVFR = fields['CVUMCVFR'],
        CVUMAUDT = td.date().tointeger(),
        CVUMAUTM = td.time().tointeger(),
        CVUMAUUS = mvcsession.cookies['user_name'].encode('utf8')
      )
      if not session.transaction_started():
        session.begin()
      try:
        session.save(rec1)
        session.commit()
      except:
        session.rollback()
        session.expunge(rec1)
        raise
      if fields['CVUMCVRV'] == 1:
        q = UOMCVT.query
        q = q.filter_by(CVUMUMCD = fields['CVUMALCD'])
        q = q.filter_by(CVUMALCD = fields['CVUMUMCD'])
        obj = q.first()
        if not obj:
          if fields['CVUMCVFR'] == '*':
            cvfr = '/'
          else:
            cvfr = '*'

          rec2 = UOMCVT(
            CVUMCONO = fields['CVUMCONO'],
            CVUMUMCD = rec1.CVUMALCD,
            CVUMUMNM = rec1.CVUMALNM,
            CVUMALCD = rec1.CVUMUMCD,
            CVUMALNM = rec1.CVUMUMNM,
            CVUMCVFA = rec1.CVUMCVFA,
            CVUMCVFR = cvfr,
            CVUMAUDT = td.date().tointeger(),
            CVUMAUTM = td.time().tointeger(),
            CVUMAUUS = mvcsession.cookies['user_name'].encode('utf8')
          )
          if not session.transaction_started():
            session.begin()
          try:
            session.save(rec2)
            session.commit()
          except:
            session.rollback()
            session.expunge(rec2)
            raise

    if (mvcsession.execType == MVCExecEdit):
      if not obj:
        raise Exception('Record could not be found')
      mvcsession.entryDataset.CopyIntoORM(
        'CVUMCVFA;CVUMCVFR',
        'CVUMCVFA;CVUMCVFR',
        obj)
      obj.CVUMAUDT = td.date().tointeger()
      obj.CVUMAUTM = td.time().tointeger()
      obj.CVUMAUUS = mvcsession.cookies['user_name'].encode('utf8')
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
      session.delete(obj)
      session.commit()
    return mvcsession


