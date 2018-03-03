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
from tbl import EFUGRP

class SES011(MVCController):
  """
  User group management
  """

  _description = 'User group'
  _supported_functions = (MVCFuncNew, MVCFuncOpen, MVCFuncShow, MVCFuncCopy, MVCFuncDelete)
  _model_binder = MVCModelBinder(EFUGRP)

  EFUGGRID    = MVCField(MVCTypeList + MVCTypeField + MVCTypeParam, String(24), label='Group', synchronized=True, browseable=True, charcase=ecUpperCase)
  EFUGUSID    = MVCField(MVCTypeList + MVCTypeField, String(24), label='User', synchronized=True, browseable=True, charcase=ecUpperCase)
  EFUGFSNM    = MVCField(MVCTypeList + MVCTypeField, String(24), label='First name', enabled=False)
  EFUGLSNM    = MVCField(MVCTypeList + MVCTypeField, String(24), label='Last name', enabled=False)

  def lookupView(self, mvcsession, fieldName):
    '''Define lookup metadata for specified field'''
    ret = MVCLookupDef('','')
    if fieldName == 'EFUGGRID':
      ret.svcname = 'SES010'
      ret.params = {'EFUSUSTP':'%v:GRP', 'UFUSSTAT': '%v:1'}
      ret.retfield = 'EFUSUSID'
    if fieldName == 'EFUGUSID':
      ret.svcname = 'SES010'
      ret.params = {'EFUSUSTP':'%v:USR', 'UFUSSTAT': '%v:1'}
      ret.retfield = 'EFUSUSID'
    return ret

  def initializeData(self, mvcsession):
    '''Initializing data'''
    params = mvcsession.paramDataset.FieldsAsDict()
    mvcsession.entryDataset.Append()
    mvcsession.entryDataset.SetFieldValue('EFUGGRID', params['EFUGGRID'])
    mvcsession.entryDataset.Post()
    return mvcsession

  def initializeParam(self, mvcsession, query):
    '''Initialize parameters'''
    params = mvcsession.paramDataset.FieldsAsDict()
    validators.NotEmpty(messages={'empty':'Parameter is empty'}).to_python(params['EFUGGRID'])
    proxy = self.getBusinessObjectProxy()
    usrobj = proxy.getObject('USROBJ')
    validators.NotEmpty(messages={'empty':'Group is invalid'}).to_python(usrobj.validateGroup(params['EFUGGRID']))
    if (params['EFUGGRID'] not in ('', None)):
      query = query.filter_by(EFUGGRID = params['EFUGGRID'])
    else:
      raise Exception('')
    return query

  def synchronizeData(self, mvcsession, fieldName, fieldType):
    '''Synchronize data retrieved from user input'''
    fields = mvcsession.entryDataset.FieldsAsDict()
    proxy = self.getBusinessObjectProxy()
    usrobj = proxy.getObject('USROBJ')
    if (fieldName == 'UFUGGRID') and (fields['EFUGGRID'] not in (None, '')):
      usrobj.validateGroup(fields['EFUGGRID'])
    if (fieldName == 'EFUGUSID'):
      val = usrobj.getUserInfo(fields['EFUGUSID'])
      mvcsession.entryDataset.Edit()
      mvcsession.entryDataset.SetFieldValue('EFUGFSNM', val[0])
      mvcsession.entryDataset.SetFieldValue('EFUGLSNM', val[1])
      mvcsession.entryDataset.SetFieldValue('EFUGUSID', val[3])
      mvcsession.entryDataset.Post()
    return mvcsession

  def validateData(self, mvcsession):
    '''Validate date retrieved from user input before storing it into persistent storage'''
    fields = mvcsession.entryDataset.FieldsAsDict()
    validators.NotEmpty(messages ={'empty':'Group must not empty'}).to_python(fields['EFUGGRID'])
    validators.NotEmpty(messages ={'empty':'User must not empty'}).to_python(fields['EFUGUSID'])
    return mvcsession








