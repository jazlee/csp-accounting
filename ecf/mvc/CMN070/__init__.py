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
from tbl import NUMTYP

class CMN070(MVCController):
  """
  Numbering Type
  """

  _description = 'Numbering Type'
  _supported_functions = (MVCFuncSelect, MVCFuncNew, MVCFuncOpen, MVCFuncShow, MVCFuncCopy, MVCFuncDelete)
  _model_binder = MVCModelBinder(NUMTYP)

  NMTPCONO  = MVCField(MVCTypeList + MVCTypeField + MVCTypeParam , String(3), label='Comp. No',enabled=False, visible=False)
  NMTPNOID  = MVCField(MVCTypeList + MVCTypeField, String(3), label='Type. ID', charcase=ecUpperCase)
  NMTPNONM  = MVCField(MVCTypeList + MVCTypeField, String(16), label='Name', synchronized=True)
  NMTPNODS  = MVCField(MVCTypeList + MVCTypeField, String(48), label='Description')

  def initView(self, mvcsession):
    '''Initialize the program'''
    mvcsession.selectFunction = MVCExtFunction('xxx', 'CMN075', \
        params = {
          'NMSRCONO':'%f:NMTPCONO',
          'NMSRNOID':'%f:NMTPNOID'
        }, autoSelect=False
      )
    mvcsession.extFunctions = ( MVCExtFunction('Numbering Series', 'CMN075',
        params = {
          'NMSRCONO':'%f:NMTPCONO',
          'NMSRNOID':'%f:NMTPNOID'
        }),
      )
    return mvcsession

  def synchronizeData(self, mvcsession, fieldName, fieldType):
    '''Synchronize data retrieved from user input'''
    fields = mvcsession.entryDataset.FieldsAsDict()
    if (fieldName == 'NMTPNONM') and \
       (fields['NMTPNONM'] not in (None, '')) and \
       (fields['NMTPNODS'] in (None, '')):
      mvcsession.entryDataset.Edit()
      mvcsession.entryDataset.SetFieldValue('NMTPNODS', fields['NMTPNONM'])
      mvcsession.entryDataset.Post()
    return mvcsession


  def initializeParam(self, mvcsession, query):
    '''Initialize parameters'''
    params = mvcsession.paramDataset.FieldsAsDict()
    proxy = self.getBusinessObjectProxy()
    if params['NMTPCONO'] is None:
      usrobj = proxy.getObject('USROBJ')
      infodict = usrobj.retrieveUserInfoDict(mvcsession)
      params['NMTPCONO'] = infodict['USRCONO']

      mvcsession.paramDataset.Edit()
      mvcsession.paramDataset.SetFieldValues(params)
      mvcsession.paramDataset.Post()

    cmpobj = proxy.getObject('CMPOBJ')
    cmpobj.validateCompany(params['NMTPCONO'])

    query = query.filter_by(NMTPCONO = params['NMTPCONO'])
    return query

  def initializeData(self, mvcsession):
    '''Initializing data'''
    params = mvcsession.paramDataset.FieldsAsDict()
    mvcsession.entryDataset.Append()
    mvcsession.entryDataset.SetFieldValues(params)
    mvcsession.entryDataset.Post()
    return mvcsession

  def synchronizeData(self, mvcsession, fieldName, fieldType):
    '''Synchronize data retrieved from user input'''
    fields = mvcsession.entryDataset.FieldsAsDict()
    if (fieldName == 'NMTPNONM') and \
       (fields['NMTPNONM'] not in (None, '')) and \
       (fields['NMTPNODS'] in (None, '')):
      mvcsession.entryDataset.Edit()
      mvcsession.entryDataset.SetFieldValue('NMTPNODS', fields['NMTPNONM'])
      mvcsession.entryDataset.Post()
    return mvcsession
