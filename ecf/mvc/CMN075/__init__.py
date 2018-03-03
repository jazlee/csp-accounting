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
from tbl import NUMSER

class CMN075(MVCController):
  """
  Numbering Series
  """

  _description = 'Numbering Series'
  _supported_functions = (MVCFuncNew, MVCFuncOpen, MVCFuncShow, MVCFuncCopy)
  _model_binder = MVCModelBinder(NUMSER)

  NMSRCONO  = MVCField(MVCTypeList + MVCTypeField + MVCTypeParam , String(3), label='Comp. No',
                enabled=False, visible=False)
  NMSRNOID  = MVCField(MVCTypeList + MVCTypeField + MVCTypeParam , String(4), label='No. ID', synchronized=True, browseable=True, charcase = ecUpperCase)
  NMSRFRDT  = MVCField(MVCTypeList + MVCTypeField, Date, label='From Date')
  NMSRMINO  = MVCField(MVCTypeField, Integer, label='Minimum Number')
  NMSRMXNO  = MVCField(MVCTypeList + MVCTypeField, Integer, label='Maximum Number')
  NMSRLSNO  = MVCField(MVCTypeList + MVCTypeField, Integer, label='Last Number Used', enabled=False)
  NMSRPFCD  = MVCField(MVCTypeField, String(3), label='Prefix Used')
  NMSRSFCD  = MVCField(MVCTypeField, String(3), label='Suffix Used')


  def lookupView(self, mvcsession, fieldName):
    '''Define lookup metadata for specified field'''
    ret = MVCLookupDef('','')
    if (fieldName == 'NMSRNOID'):
      ret.svcname = 'CMN070'
      ret.retfield = 'NMTPNOID'
    return ret


  def synchronizeData(self, mvcsession, fieldName, fieldType):
    '''Synchronize data retrieved from user input'''
    dataset = mvcsession.entryDataset if fieldType == MVCTypeField else \
      mvcsession.paramDataset
    fields = dataset.FieldsAsDict()
    proxy = self.getBusinessObjectProxy()
    if (fieldName == 'NMSRNOID'):
      numobj = proxy.getObject('NUMOBJ')
      restuple = numobj.getNumberingCode(fields['NMSRCONO'], fields['NMSRNOID'])

      if restuple[0] is None:
        raise Exception ('Numbering type could not be found')
    return mvcsession

  def initializeParam(self, mvcsession, query):
    '''Initialize parameters'''
    params = mvcsession.paramDataset.FieldsAsDict()
    proxy = self.getBusinessObjectProxy()
    if params['NMSRCONO'] is None:
      usrobj = proxy.getObject('USROBJ')
      infodict = usrobj.retrieveUserInfoDict(mvcsession)
      params['NMSRCONO'] = infodict['USRCONO']

      mvcsession.paramDataset.Edit()
      mvcsession.paramDataset.SetFieldValues(params)
      mvcsession.paramDataset.Post()

    cmpobj = proxy.getObject('CMPOBJ')
    cmpobj.validateCompany(params['NMSRCONO'])

    query = query.filter_by(NMSRCONO = params['NMSRCONO'])
    if params['NMSRNOID'] not in (None, ''):
      query = query.filter_by(NMSRNOID = params['NMSRNOID'])
    return query

  def initializeData(self, mvcsession):
    '''Initializing data'''
    params = mvcsession.paramDataset.FieldsAsDict()
    mvcsession.entryDataset.Append()
    mvcsession.entryDataset.SetFieldValues(params)
    mvcsession.entryDataset.SetFieldValue('NMSRFRDT', dt.date.today().tointeger())
    mvcsession.entryDataset.SetFieldValue('NMSRMINO', 0)
    mvcsession.entryDataset.SetFieldValue('NMSRMXNO', 999999)
    mvcsession.entryDataset.SetFieldValue('NMSRLSNO', 0)
    mvcsession.entryDataset.Post()
    return mvcsession
