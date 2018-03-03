"""
G/L Account Cluster Identification
"""

__author__    = 'Jaimy Azle'
__version__   = '1.0'
__copyright__ = 'Copyright (c) 2008 Jaimy Azle'

from mvcsvc import *
from elixir import *
import datetime as dt
import sqlalchemy as sa
from validators import *
from tbl import GLSCSI

class GLS020(MVCController):
  """
  G/L Account Cluster Identification
  """

  _description = 'Cluster Identification'
  _supported_functions = (MVCFuncNew, MVCFuncOpen, MVCFuncShow, MVCFuncCopy, MVCFuncDelete)
  _model_binder = MVCModelBinder(GLSCSI)

  CSSICSID  = MVCField(MVCTypeList + MVCTypeField + MVCTypeParam, Integer(), label='Cluster ID',
    choices={'01':1, '02':2, '03':3, '04':4, '05':5, '06':6, '07':7, '08':8, '09':9, '10':10}, synchronized=True)
  CSSICSNM  = MVCField(MVCTypeParam, String(32), label='Cluster Name', enabled=False)
  CSSICSCD  = MVCField(MVCTypeList + MVCTypeField, String(48), label='Code')
  CSSICSDS  = MVCField(MVCTypeList + MVCTypeField, String(48), label='Name')
  CSSICUCD  = MVCField(MVCTypeList + MVCTypeField, String(48), label='Closing account', browseable=True, synchronized=True)
  CSSICUNM  = MVCField(MVCTypeField, String(32), label='Account Name', enabled=False)

  def lookupView(self, session, fieldName):
    ret = MVCLookupDef('','')
    if fieldName == 'CSSICUCD':
      ret.svcname = 'GLS450'
      ret.retfield = 'GLACACFM'
    return ret

  def synchronizeData(self, mvcsession, fieldName, fieldType):
    dataset = mvcsession.entryDataset if fieldType == MVCTypeField else \
      mvcsession.paramDataset
    fields = dataset.FieldsAsDict()
    proxy = self.getBusinessObjectProxy()
    if (fieldName == 'CSSICSID') and (fields['CSSICSID'] not in (None, 0)):
      glsobj = proxy.getObject('GLSOBJ')
      obj = glsobj.getAcctCluster(fields['CSSICSID'])
      if obj['CSCPCSID'] is None:
        raise Exception('Cluster ID is not defined')
      if fieldType != MVCTypeField:
        dataset.Edit()
        dataset.SetFieldValue('CSSICSNM', obj['CSCPCSNM'])
        dataset.Post()

    if (fieldName == 'CSSICUCD') and (fields['CSSICUCD'] not in (None, '')):
      usrobj = proxy.getObject('USROBJ')
      glsobj = proxy.getObject('GLSOBJ')
      info = usrobj.retrieveUserInfoDict(mvcsession)
      cono = info['USRCONO']
      acct = glsobj.getAcct(cono, acct)

      dataset.Edit()
      dataset.SetFieldValue('CSSICUCD', acct['GLACACFM'])
      dataset.SetFieldValue('CSSICUNM', acct['GLACACNM'])
      dataset.Post()
    return mvcsession

  def initializeParam(self, mvcsession, query):
    '''Initialize parameters'''
    params = mvcsession.paramDataset.FieldsAsDict()
    proxy = self.getBusinessObjectProxy()
    if (params['CSSICSID'] is None):
      params['CSSICSID'] = 1

      mvcsession.paramDataset.Edit()
      mvcsession.paramDataset.SetFieldValues(params)
      mvcsession.paramDataset.Post()

    return query

  def afterRetrieveData(self, mvcsession, obj):
    '''Event triggered after retrieving data'''

    if mvcsession.execType == MVCExecEdit:
      mvcsession.fieldDefs.CSSICSID.enabled = False
      mvcsession.fieldDefs.CSSICSCD.enabled = False

    return (mvcsession, obj)

  def validateData(self, mvcsession):
    '''Validate data retrieved from user input before storing it into persistent storage'''
    fields = mvcsession.entryDataset.FieldsAsDict()
    validators.NotEmpty(messages={'empty': 'Account cluster id must not empty'}).to_python(fields['CSSICSID'])
    validators.NotEmpty(messages={'empty': 'Cluster code must not empty'}).to_python(fields['CSSICSCD'])

    proxy = self.getBusinessObjectProxy()
    glsobj = proxy.getObject('GLSOBJ')
    cluster = glsobj.getAcctCluster(fields['CSSICSID'])
    if cluster['CSCPCSID'] is None:
      raise Exception('Cluster id [%d] is not defined' % fields['CSSICSID'])

    return mvcsession

  def beforePostData(self, mvcsession, obj):
    '''Event triggered before posting data'''
    fields = mvcsession.entryDataset.FieldsAsDict()

    proxy = self.getBusinessObjectProxy()
    glsobj = proxy.getObject('GLSOBJ')
    cluster = glsobj.getAcctCluster(fields['CSSICSID'])

    if mvcsession.execType in (MVCExecEdit, MVCExecCopy, MVCExecAppend):
      cccode = fields['CSSICSCD']
      if len(cccode) > cluster['CSCPCSLN']:
        cccode = cccode[:cluster['CSCPCSLN']]
      elif len(cccode) < cluster['CSCPCSLN']:
        cnt = cluster['CSCPCSLN'] - len(cccode)
        st = "%%.%dd%s" % (cnt, cccode)
        cccode = st % 0

      fields['CSSICSCD'] = cccode

      mvcsession.entryDataset.Edit()
      mvcsession.entryDataset.SetFieldValues(fields)
      mvcsession.entryDataset.Post()

    return (mvcsession, obj)


