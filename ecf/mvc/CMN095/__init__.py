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
from tbl import FSCPRD

class CMN095(MVCController):
  """
  Fiscal Period
  """

  _description = 'Fiscal Period'
  _supported_functions = (MVCFuncNew, MVCFuncOpen, MVCFuncShow, MVCFuncCopy, MVCFuncDelete)
  _model_binder = MVCModelBinder(FSCPRD)

  FSPRCONO  = MVCField(MVCTypeList + MVCTypeField + MVCTypeParam, String(3), label='Comp. ID', visible=False, enabled=False)
  FSPRTPCD  = MVCField(MVCTypeList + MVCTypeField + MVCTypeParam, String(3), label='Fiscal Type', visible=False, enabled=False)
  FSPRFSYR  = MVCField(MVCTypeList + MVCTypeField + MVCTypeParam, Integer, label='Year', enabled=False)
  FSPRPRID  = MVCField(MVCTypeList + MVCTypeField, Integer, label='Period')
  FSPRPRNM  = MVCField(MVCTypeList + MVCTypeField, String(16), label='Name')
  FSPRFRDT  = MVCField(MVCTypeList + MVCTypeField, Date, label='Fr. Date')
  FSPRTODT  = MVCField(MVCTypeList + MVCTypeField, Date, label='To Date')
  FSPRPRST  = MVCField(MVCTypeList + MVCTypeField, Integer, label='Closed', index=True)

  def initializeParam(self, mvcsession, query):
    '''Initialize parameters'''
    params = mvcsession.paramDataset.FieldsAsDict()
    proxy = self.getBusinessObjectProxy()
    if params['FSPRCONO'] in (None, ''):
      usrobj = proxy.getObject('USROBJ')
      infodict = usrobj.retrieveUserInfoDict(mvcsession)
      params['FSPRCONO'] = infodict['USRCONO']

      mvcsession.paramDataset.Edit()
      mvcsession.paramDataset.SetFieldValues(params)
      mvcsession.paramDataset.Post()

    cmpobj = proxy.getObject('CMPOBJ')
    cmpobj.validateCompany(params['FSPRCONO'])

    if (params['FSPRTPCD'] is None) or (params['FSPRFSYR'] is None):
      raise Exception('This program could not be loaded directly by user');
    query = query.filter_by(FSPRCONO = params['FSPRCONO'])
    query = query.filter_by(FSPRTPCD = params['FSPRTPCD'])
    query = query.filter_by(FSPRFSYR = params['FSPRFSYR'])
    return query

  def initializeData(self, mvcsession):
    '''Initializing data'''
    params = mvcsession.paramDataset.FieldsAsDict()
    mvcsession.entryDataset.Append()
    mvcsession.entryDataset.SetFieldValues(params)
    mvcsession.entryDataset.Post()
    return mvcsession

  def validateData(self, mvcsession):
    '''Validate data retrieved from user input before storing it into persistent storage'''
    fields = mvcsession.entryDataset.FieldsAsDict()
    proxy = self.getBusinessObjectProxy()
    fscobj = proxy.getObject('FSCOBJ')
    fscinfo = fscobj.getFiscalYear(fields['FSPRCONO'], fields['FSPRTPCD'], fields['FSPRFSYR'])
    if fscinfo[0]:
      if fields['FSPRPRID'] > fscinfo[0]:
        raise Exception('Period must not over than total period count allowed')
    else:
      raise Exception('Header record could not be retrieved')
    return mvcsession







