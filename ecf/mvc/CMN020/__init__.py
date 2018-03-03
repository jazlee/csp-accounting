"""
States, this module purposed for maintain state list reference needed
by various modules on this system.
"""
__author__    = 'Jaimy Azle'
__version__   = '1.0'
__copyright__ = 'Copyright (c) 2008 Jaimy Azle'

from mvcsvc import *
from elixir import *
from tbl import MSTSTA

class CMN020(MVCController):
  """
  States, this module purposed for maintain state list reference needed
  by various modules on this system.
  """

  _description = 'States'
  _supported_functions = (MVCFuncNew, MVCFuncOpen, MVCFuncShow, MVCFuncDelete)
  _model_binder = MVCModelBinder(MSTSTA)

  CMSTCONO  = MVCField(MVCTypeList + MVCTypeField + MVCTypeParam, String(3), label='Comp. ID',
                enabled=False, visible=False)
  CMSTIDCD  = MVCField(MVCTypeList + MVCTypeField, String(6), label='State', charcase=ecUpperCase)
  CMSTIDNM  = MVCField(MVCTypeList + MVCTypeField, String(16), label='Name', synchronized=True)
  CMSTIDDS  = MVCField(MVCTypeList + MVCTypeField, String(32), label='Description')

  def initializeParam(self, mvcsession, query):
    '''Initialize parameters'''
    params = mvcsession.paramDataset.FieldsAsDict()
    proxy = self.getBusinessObjectProxy()
    if params['CMSTCONO'] in (None, ''):
      usrobj = proxy.getObject('USROBJ')
      infodict = usrobj.retrieveUserInfoDict(mvcsession)
      params['CMSTCONO'] = infodict['USRCONO']

      mvcsession.paramDataset.Edit()
      mvcsession.paramDataset.SetFieldValue('CMSTCONO', params['CMSTCONO'])
      mvcsession.paramDataset.Post()

    cmpobj = proxy.getObject('CMPOBJ')
    cmpobj.validateCompany(params['CMSTCONO'])

    query = query.filter_by(CMSTCONO = params['CMSTCONO'])
    return query

  def initializeData(self, mvcsession):
    '''Initializing data'''
    params = mvcsession.paramDataset.FieldsAsDict()
    mvcsession.entryDataset.Append()
    mvcsession.entryDataset.SetFieldValue('CMSTCONO', params['CMSTCONO'])
    mvcsession.entryDataset.Post()
    return mvcsession

  def synchronizeData(self, mvcsession, fieldName, fieldType):
    '''Synchronize data retrieved from user input'''
    fields = mvcsession.entryDataset.FieldsAsDict()
    if (fieldName == 'CMSTIDNM') and \
       (fields['CMSTIDNM'] not in ('', None)) and \
       (fields['CMSTIDDS'] in ('', None)):
      mvcsession.entryDataset.Edit()
      mvcsession.entryDataset.SetFieldValue('CMSTIDDS', fields['CMSTIDNM'])
      mvcsession.entryDataset.Post()
    return mvcsession
