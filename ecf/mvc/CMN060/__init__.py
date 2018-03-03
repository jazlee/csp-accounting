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

from mvcsvc import *
from elixir import *
import datetime as dt
import sqlalchemy as sa
from validators import *
from tbl import MSTUOM

class CMN060(MVCController):
  """
  Unit of measurement
  """

  _description = 'Unit of Measurement'
  _supported_functions = (MVCFuncSelect, MVCFuncNew, MVCFuncOpen, MVCFuncShow, MVCFuncCopy, MVCFuncDelete)
  _model_binder = MVCModelBinder(MSTUOM)

  CMUMCONO  = MVCField(MVCTypeList + MVCTypeField + MVCTypeParam, String(3), label='Comp. ID',
                enabled=False, visible=False)
  CMUMUMCD  = MVCField(MVCTypeList + MVCTypeField, String(3), label='U/M Code', charcase=ecUpperCase)
  CMUMUMNM  = MVCField(MVCTypeList + MVCTypeField, String(24), label='Name', synchronized=True)
  CMUMUMDS  = MVCField(MVCTypeField, String(48), label='Description')

  def initView(self, mvcsession):
    '''Initialize the program'''
    mvcsession.selectFunction = MVCExtFunction('xxx', 'CMN065', params = {'CVUMUMCD':'%f:CMUMUMCD'}, autoSelect=False)
    mvcsession.extFunctions = ( MVCExtFunction('U/M Conversion Table', 'CMN065', params = {'CVUMUMCD':'%f:CMUMUMCD'}), )
    return mvcsession

  def synchronizeData(self, mvcsession, fieldName, fieldType):
    '''Synchronize data retrieved from user input'''
    fields = mvcsession.entryDataset.FieldsAsDict()
    if (fieldName == 'CMUMUMNM') and \
       (fields['CMUMUMNM'] not in (None, '')) and \
       (fields['CMUMUMDS'] in (None, '')):
      mvcsession.entryDataset.Edit()
      mvcsession.entryDataset.SetFieldValue('CMUMUMDS', fields['CMUMUMNM'])
      mvcsession.entryDataset.Post()
    return mvcsession

  def initializeParam(self, mvcsession, query):
    '''Initialize parameters'''
    params = mvcsession.paramDataset.FieldsAsDict()
    proxy = self.getBusinessObjectProxy()
    if params['CMUMCONO'] in (None, ''):
      usrobj = proxy.getObject('USROBJ')
      infodict = usrobj.retrieveUserInfoDict(mvcsession)
      params['CMUMCONO'] = infodict['USRCONO']

      mvcsession.paramDataset.Edit()
      mvcsession.paramDataset.SetFieldValue('CMUMCONO', params['CMUMCONO'])
      mvcsession.paramDataset.Post()

    cmpobj = proxy.getObject('CMPOBJ')
    cmpobj.validateCompany(params['CMUMCONO'])

    query = query.filter_by(CMUMCONO = params['CMUMCONO'])
    return query

  def initializeData(self, mvcsession):
    '''Initializing data'''
    params = mvcsession.paramDataset.FieldsAsDict()
    mvcsession.entryDataset.Append()
    mvcsession.entryDataset.SetFieldValue('CMUMCONO', params['CMUMCONO'])
    mvcsession.entryDataset.Post()
    return mvcsession




