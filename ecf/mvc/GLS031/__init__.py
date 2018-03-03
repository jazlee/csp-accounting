"""
G/L Detail Account Structure
"""

__author__    = 'Jaimy Azle'
__version__   = '1.0'
__copyright__ = 'Copyright (c) 2008 Jaimy Azle'

from mvcsvc import *
from elixir import *
import datetime as dt
import sqlalchemy as sa
from validators import *
from tbl import GLSACI

class GLS031(MVCController):
  """
  G/L Detail Account Structure
  """

  _description = 'Detail Account Structure'
  _supported_functions = (MVCFuncNew, MVCFuncOpen, MVCFuncShow, MVCFuncDelete)
  _model_binder = MVCModelBinder(GLSACI)

  AIASACCD  = MVCField(MVCTypeList + MVCTypeField + MVCTypeParam, String(8), label='Struct. Code', enabled=False)
  AIASCSID  = MVCField(MVCTypeList + MVCTypeField, Integer(), label='Cluster ID',
    choices={'01':1, '02':2, '03':3, '04':4, '05':5, '06':6, '07':7, '08':8, '09':9, '10':10},
    synchronized=True)
  AIASCSNM  = MVCField(MVCTypeList + MVCTypeField, String(32), label='Cluster Name', enabled=False)
  AIASCSIX  = MVCField(MVCTypeList + MVCTypeField, String(32), label='Seq. No')

  def initView(self, mvcsession):
    mvcsession.extFunctions = ( MVCExtFunction('Account Cluster Definition', 'GLS010'),)
    return mvcsession

  def synchronizeData(self, mvcsession, fieldName, fieldType):
    '''Synchronize data retrieved from user input'''
    dataset = mvcsession.entryDataset if fieldType == MVCTypeField else \
      mvcsession.paramDataset
    fields = dataset.FieldsAsDict()
    proxy = self.getBusinessObjectProxy()
    if (fieldName == 'AIASCSID') and (fields['AIASCSID'] not in(0, None)):
      glsobj = proxy.getObject('GLSOBJ')
      acctstruct = glsobj.getAcctCluster(fields['AIASCSID'])
      if acctstruct['CSCPCSID'] is None:
        raise Exception('Cluster ID is not defined')
      mvcsession.entryDataset.Edit()
      mvcsession.entryDataset.SetFieldValue('AIASCSNM', acctstruct['CSCPCSNM'])
      mvcsession.entryDataset.Post()
    return mvcsession

  def initializeParam(self, mvcsession, query):
    '''Initialize parameters'''
    params = mvcsession.paramDataset.FieldsAsDict()
    proxy = self.getBusinessObjectProxy()
    if (params['AIASACCD'] is None):
      raise Exception('Program GLS031 could not be load directly by user')

    query = query.filter_by(AIASACCD = params['AIASACCD'])
    query = query.order_by(sa.asc(GLSACI.AIASACCD))
    query = query.order_by(sa.asc(GLSACI.AIASCSIX))
    return query

  def initializeData(self, mvcsession):
    '''Initializing data'''
    params = mvcsession.paramDataset.FieldsAsDict()
    proxy = self.getBusinessObjectProxy()
    params['AIASCSIX'] = 0
    mvcsession.entryDataset.Append()
    mvcsession.entryDataset.SetFieldValues(params)
    mvcsession.entryDataset.Post()
    return mvcsession

  def validateData(self, mvcsession):
    '''Validate data retrieved from user input before storing it into persistent storage'''
    fields = mvcsession.entryDataset.FieldsAsDict()
    validators.NotEmpty(messages={'empty': 'Structure code must not empty'}).to_python(fields['AIASACCD'])
    validators.NotEmpty(messages={'empty': 'Cluster id must not empty'}).to_python(fields['AIASCSID'])
    return mvcsession


