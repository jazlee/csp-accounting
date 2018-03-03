"""
Area, which could mean town/district. This module this module purposed for
maintaining area list reference needed by various modules on this system.
"""
__author__    = 'Jaimy Azle'
__version__   = '1.0'
__copyright__ = 'Copyright (c) 2008 Jaimy Azle'

from mvcsvc import *
from elixir import *
import sqlalchemy as sa
import datetime as dt
from validators import *
from tbl import MSTARE

class CMN030(MVCController):
  """
  Area, which could mean town/district. This module this module purposed for
  maintaining area list reference needed by various modules on this system.
  """

  _description = 'Area'
  _supported_functions = (MVCFuncNew, MVCFuncOpen, MVCFuncShow, MVCFuncCopy, MVCFuncDelete)
  _model_binder = MVCModelBinder(MSTARE)

  CMARCONO  = MVCField(MVCTypeList + MVCTypeField + MVCTypeParam, String(3), label='Comp. ID',
                enabled=False, visible=False)
  CMARIDCD  = MVCField(MVCTypeList + MVCTypeField, String(6), label='Area', charcase=ecUpperCase)
  CMARIDNM  = MVCField(MVCTypeList + MVCTypeField, String(24), label='Name', synchronized=True)
  CMARIDDS  = MVCField(MVCTypeField, String(128), label='Description')

  def initializeParam(self, mvcsession, query):
    '''Initialize parameters'''
    params = mvcsession.paramDataset.FieldsAsDict()
    proxy = self.getBusinessObjectProxy()
    if params['CMARCONO'] in (None, ''):
      usrobj = proxy.getObject('USROBJ')
      infodict = usrobj.retrieveUserInfoDict(mvcsession)
      params['CMARCONO'] = infodict['USRCONO']

      mvcsession.paramDataset.Edit()
      mvcsession.paramDataset.SetFieldValue('CMARCONO', params['CMARCONO'])
      mvcsession.paramDataset.Post()

    cmpobj = proxy.getObject('CMPOBJ')
    cmpobj.validateCompany(params['CMARCONO'])

    query = query.filter_by(CMARCONO = params['CMARCONO'])
    return query

  def initializeData(self, mvcsession):
    '''Initializing data'''
    params = mvcsession.paramDataset.FieldsAsDict()
    mvcsession.entryDataset.Append()
    mvcsession.entryDataset.SetFieldValue('CMARCONO', params['CMARCONO'])
    mvcsession.entryDataset.Post()
    return mvcsession

  def synchronizeData(self, mvcsession, fieldName, fieldType):
    '''Synchronize data retrieved from user input'''
    fields = mvcsession.entryDataset.FieldsAsDict()
    if (fieldName == 'CMARIDNM') and \
       (fields['CMARIDNM'] not in ('', None)) and \
       (fields['CMARIDDS'] in ('', None)):
      mvcsession.entryDataset.Edit()
      mvcsession.entryDataset.SetFieldValue('CMARIDDS', fields['CMARIDNM'])
      mvcsession.entryDataset.Post()
    return mvcsession
