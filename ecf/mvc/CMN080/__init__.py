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
from tbl import FSCTYP

class CMN080(MVCController):
  """
  Fiscal Type
  """

  _description = 'Fiscal Type'
  _supported_functions = (MVCFuncSelect, MVCFuncNew, MVCFuncOpen, MVCFuncShow, MVCFuncCopy, MVCFuncDelete)
  _model_binder = MVCModelBinder(FSCTYP)

  FSTPCONO  = MVCField(MVCTypeField + MVCTypeList + MVCTypeParam, String(3), label='Comp. ID',
                enabled=False, visible=False)
  FSTPTPCD  = MVCField(MVCTypeField + MVCTypeList, String(3), label='Fiscal Type', charcase=ecUpperCase)
  FSTPTPNM  = MVCField(MVCTypeField + MVCTypeList, String(24), label='Fiscal Name', synchronized=True)
  FSTPTPDS  = MVCField(MVCTypeField + MVCTypeList, String(48), label='Description')
  FSTPPRCT  = MVCField(MVCTypeField + MVCTypeList, Integer, label='Period count', enabled=False)

  def initView(self, mvcsession):
    '''Initialize the program'''
    mvcsession.selectFunction = MVCExtFunction('xxx', 'CMN090', \
        params = {
          'FSYRCONO':'%f:FSTPCONO',
          'FSYRTPCD':'%f:FSTPTPCD'
        }, autoSelect=False
      )
    mvcsession.extFunctions = ( MVCExtFunction('Fiscal Year', 'CMN090',
        params = {
          'FSYRCONO':'%f:FSTPCONO',
          'FSYRTPCD':'%f:FSTPTPCD'
        }),
      )
    return mvcsession


  def synchronizeData(self, mvcsession, fieldName, fieldType):
    '''Synchronize data retrieved from user input'''
    fields = mvcsession.entryDataset.FieldsAsDict()
    if (fieldName == 'FSTPTPNM') and \
       (fields['FSTPTPNM'] not in (None, '')) and \
       (fields['FSTPTPDS'] in (None, '')):
      mvcsession.entryDataset.Edit()
      mvcsession.entryDataset.SetFieldValue('FSTPTPDS', fields['FSTPTPNM'])
      mvcsession.entryDataset.Post()
    return mvcsession


  def initializeParam(self, mvcsession, query):
    '''Initialize parameters'''
    params = mvcsession.paramDataset.FieldsAsDict()
    proxy = self.getBusinessObjectProxy()
    if params['FSTPCONO'] in (None, ''):
      usrobj = proxy.getObject('USROBJ')
      infodict = usrobj.retrieveUserInfoDict(mvcsession)
      params['FSTPCONO'] = infodict['USRCONO']

      mvcsession.paramDataset.Edit()
      mvcsession.paramDataset.SetFieldValue('FSTPCONO', params['FSTPCONO'])
      mvcsession.paramDataset.Post()

    cmpobj = proxy.getObject('CMPOBJ')
    cmpobj.validateCompany(params['FSTPCONO'])

    query = query.filter_by(FSTPCONO = params['FSTPCONO'])
    return query

  def initializeData(self, mvcsession):
    '''Initializing data'''
    params = mvcsession.paramDataset.FieldsAsDict()
    mvcsession.entryDataset.Append()
    mvcsession.entryDataset.SetFieldValue('FSTPCONO', params['FSTPCONO'])
    mvcsession.entryDataset.SetFieldValue('FSTPPRCT', 12)
    mvcsession.entryDataset.Post()
    return mvcsession


