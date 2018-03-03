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
from tbl import FSCFYR, FSCPRD

class CMN090(MVCController):
  """
  Fiscal Years
  """

  _description = 'Fiscal Years'
  _supported_functions = (MVCFuncSelect, MVCFuncNew, MVCFuncOpen, MVCFuncShow, MVCFuncCopy, MVCFuncDelete)
  _model_binder = MVCModelBinder(FSCFYR)

  FSYRCONO =  MVCField(MVCTypeList + MVCTypeField + MVCTypeParam, String(3), label='Comp. ID', enabled=False, visible=False)
  FSYRTPCD =  MVCField(MVCTypeList + MVCTypeField + MVCTypeParam, String(3), label='Fiscal Type', charcase=ecUpperCase, browseable=True)
  FSYRFSYR =  MVCField(MVCTypeList + MVCTypeField, Integer, label='Year')
  FSYRFSNM =  MVCField(MVCTypeList + MVCTypeField, String(16), label='Fiscal Name')
  FSYRPRCT =  MVCField(MVCTypeList + MVCTypeField, Integer, label='Period Count', enabled=False)
  FSYRFSST =  MVCField(MVCTypeList + MVCTypeField, Integer, label='Active')
  FSYRADST =  MVCField(MVCTypeList + MVCTypeField, Integer, label='Accept Adjustment')
  FSYRCLST =  MVCField(MVCTypeList + MVCTypeField, Integer, label='Closed')

  def lookupView(self, mvcsession, fieldName):
    '''Define lookup metadata for specified field'''
    ret = MVCLookupDef('','')
    if fieldName == 'FSYRTPCD':
      ret.svcname = 'CMN080'
      ret.retfield = 'FSTPTPCD'
    return ret

  def initView(self, mvcsession):
    '''Initialize the program'''
    mvcsession.selectFunction = MVCExtFunction('xxx', 'CMN095', \
        params = {
          'FSPRCONO':'%f:FSYRCONO',
          'FSPRTPCD':'%f:FSYRTPCD',
          'FSPRFSYR':'%f:FSYRFSYR'
        }, autoSelect=False
      )
    mvcsession.extFunctions = ( MVCExtFunction('Fiscal Period', 'CMN095',
        params = {
          'FSPRCONO':'%f:FSYRCONO',
          'FSPRTPCD':'%f:FSYRTPCD',
          'FSPRFSYR':'%f:FSYRFSYR'
        }),
      )
    return mvcsession

  def initializeParam(self, mvcsession, query):
    '''Initialize parameters'''
    params = mvcsession.paramDataset.FieldsAsDict()
    proxy = self.getBusinessObjectProxy()
    if params['FSYRCONO'] in (None, ''):
      usrobj = proxy.getObject('USROBJ')
      infodict = usrobj.retrieveUserInfoDict(mvcsession)
      params['FSYRCONO'] = infodict['USRCONO']

      mvcsession.paramDataset.Edit()
      mvcsession.paramDataset.SetFieldValues(params)
      mvcsession.paramDataset.Post()

    cmpobj = proxy.getObject('CMPOBJ')
    cmpobj.validateCompany(params['FSYRCONO'])

    query = query.filter_by(FSYRCONO = params['FSYRCONO'])
    if params['FSYRTPCD']:
      query = query.filter_by(FSYRTPCD = params['FSYRTPCD'])
    return query

  def initializeData(self, mvcsession):
    '''Initializing data'''
    params = mvcsession.paramDataset.FieldsAsDict()
    if params['FSYRTPCD']:
      proxy = self.getBusinessObjectProxy()
      fscobj = proxy.getObject('FSCOBJ')
      fscinfo = fscobj.getFiscalType(params['FSYRCONO'], params['FSYRTPCD'])
      params['FSYRPRCT'] = fscinfo[3]

    params['FSYRFSYR'], params['FSYRFSST'] = (dt.date.today().year, 0)
    params['FSYRADST'], params['FSYRCLST'] = (0, 0)

    mvcsession.entryDataset.Append()
    mvcsession.entryDataset.SetFieldValues(params)
    mvcsession.entryDataset.Post()
    return mvcsession

  def beforePostData(self, mvcsession, obj):
    '''Event triggered before posting data'''
    fields = mvcsession.entryDataset.FieldsAsDict()
    proxy = self.getBusinessObjectProxy()
    fscobj = proxy.getObject('FSCOBJ')
    if (mvcsession.execType in (MVCExecAppend, MVCExecCopy)):
      fscobj.createFiscalPeriods(fields['FSYRCONO'], fields['FSYRTPCD'], fields['FSYRFSYR'])
    elif (mvcsession.execType == MVCExecDelete):
      fscobj.deleteFiscalPeriods(fields['FSYRCONO'], fields['FSYRTPCD'], fields['FSYRFSYR'])
    return (mvcsession, obj)

  def validateData(self, mvcsession):
    '''Validate date retrieved from user input before storing it into persistent storage'''

    fields = mvcsession.entryDataset.FieldsAsDict()
    proxy = self.getBusinessObjectProxy()
    fscobj = proxy.getObject('FSCOBJ')

    validators.NotEmpty(messages= {'empty':'Company should not be empty when creating fiscal period'}).to_python(fields['FSYRCONO'])
    validators.NotEmpty(messages= {'empty':'Fiscal type should not be empty'}).to_python(fields['FSYRTPCD'])
    validators.NotEmpty(messages= {'empty':'Fiscal year should not be empty when creating fiscal period'}).to_python(fields['FSYRFSYR'])
    fscinfo = fscobj.getFiscalType(fields['FSYRCONO'], fields['FSYRTPCD'])
    validators.NotEmpty(messages= {'empty':'Fiscal type should not be empty when creating fiscal period'}).to_python(fscinfo[0])
    return mvcsession

