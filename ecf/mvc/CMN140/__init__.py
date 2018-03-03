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
from tbl import CMPSDP, CMPDPT

class CMN140(MVCController):
  """
  Sub-Department
  """

  _description = 'Sub-Department'
  _supported_functions = (MVCFuncNew, MVCFuncOpen, MVCFuncShow, MVCFuncCopy, MVCFuncDelete)
  _model_binder = MVCModelBinder(CMPSDP)

  CMSBSBNO  = MVCField(MVCTypeField + MVCTypeList, String(4), label='Sub-Dept', charcase=ecUpperCase)
  CMSBSBNM  = MVCField(MVCTypeField + MVCTypeList, String(24), label='Name', synchronized=True)
  CMSBSBDS  = MVCField(MVCTypeField, String(48), label='Description')
  CMSBDPNO  = MVCField(MVCTypeField + MVCTypeList, String(3), label='Dept', synchronized=True, browseable=True, charcase = ecUpperCase)
  CMSBDPNM  = MVCField(MVCTypeField, String(24), label='Dept', enabled=False)
  CMSBCONO  = MVCField(MVCTypeField + MVCTypeList + MVCTypeParam, String(3), label='Comp', enabled=False)
  CMSBDVNO  = MVCField(MVCTypeField + MVCTypeList + MVCTypeParam, String(3), label='Div', enabled=False)

  def lookupView(self, mvcsession, fieldName):
    '''Define lookup metadata for specified field'''
    ret = MVCLookupDef('','')
    if fieldName == 'CMSBDPNO':
      ret.svcname = 'CMN130'
      ret.retfield = 'CMDPDPNO'
    return ret

  def initializeParam(self, mvcsession, query):
    '''Initialize parameters'''
    params = mvcsession.paramDataset.FieldsAsDict()
    proxy = self.getBusinessObjectProxy()
    if (params['CMSBCONO'] is None) or \
       (params['CMSBDVNO'] is None):

      usrobj  = proxy.getObject('USROBJ')
      usrinfo = usrobj.retrieveUserInfoDict(mvcsession)

      params['CMSBCONO'] = usrinfo['USRCONO']
      params['CMSBDVNO'] = usrinfo['USRDVNO']

      mvcsession.paramDataset.Edit()
      mvcsession.paramDataset.SetFieldValues(params)
      mvcsession.paramDataset.Post()

    cmpobj = proxy.getObject('CMPOBJ')
    cmpobj.validateCompany(params['CMSBCONO'])
    cmpobj.validateDivision(params['CMSBCONO'], params['CMSBDVNO'])

    query = query.filter_by(CMSBCONO = params['CMSBCONO'])
    query = query.filter_by(CMSBDVNO = params['CMSBDVNO'])

    return query

  def initializeData(self, mvcsession):
    '''Initializing data'''
    params = mvcsession.paramDataset.FieldsAsDict()
    proxy = self.getBusinessObjectProxy()
    mvcsession.entryDataset.Append()
    mvcsession.entryDataset.SetFieldValues(params)
    mvcsession.entryDataset.Post()
    return mvcsession

  def synchronizeData(self, mvcsession, fieldName, fieldType):
    '''Synchronize data retrieved from user input'''
    fields = mvcsession.entryDataset.FieldsAsDict()
    proxy = self.getBusinessObjectProxy()
    cmpobj = proxy.getObject('CMPOBJ')
    if (fieldName == 'CMSBSBNM') and (fields['CMSBSBNM'] is not None) and \
       (fields['CMSBSBDS'] is None):
      mvcsession.entryDataset.Edit()
      mvcsession.entryDataset.SetFieldValue('CMSBSBDS', fields['CMSBSBNM'])
      mvcsession.entryDataset.Post()
    elif (fieldName == 'CMSBDPNO'):
      dptinfo = cmpobj.getDepartment(fields['CMSBCONO'], fields['CMSBDVNO'], fields['CMSBDPNO'])

      mvcsession.entryDataset.Edit()
      mvcsession.entryDataset.SetFieldValue('CMSBCONO', dptinfo[0])
      mvcsession.entryDataset.SetFieldValue('CMSBDVNO', dptinfo[1])
      mvcsession.entryDataset.SetFieldValue('CMSBDPNO', dptinfo[2])
      mvcsession.entryDataset.SetFieldValue('CMSBDPNM', dptinfo[3])
      mvcsession.entryDataset.Post()
    return mvcsession