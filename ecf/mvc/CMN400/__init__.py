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
from tbl import SYSCAL

class CMN400(MVCController):
  """
  System Calendar
  """

  _description = 'System Calendar'
  _supported_functions = (MVCFuncNew, MVCFuncOpen, MVCFuncShow, MVCFuncCopy, MVCFuncDelete)
  _model_binder = MVCModelBinder(SYSCAL)

  SYCLCONO  = MVCField(MVCTypeList + MVCTypeField + MVCTypeParam, String(3), label='Comp. ID',
                enabled=False, visible=False)
  SYCLCLDT  = MVCField(MVCTypeList + MVCTypeField, Date, label='Date', synchronized=True)
  SYCLCLYR  = MVCField(MVCTypeField + MVCTypeParam, Integer, label='Year')
  SYCLCLMT  = MVCField(MVCTypeField + MVCTypeParam, Integer, label='Month',
                  choices={'January':1, 'February':2, 'March':3, 'April':4 ,'May':5, 'June':6,
                           'July':7, 'August':8, 'September':9, 'October':10, 'November':11 ,'December':12})
  SYCLCLDS  = MVCField(MVCTypeList + MVCTypeField, String(48), label='Description')
  SYCLCLDW  = MVCField(MVCTypeList + MVCTypeField, Integer, label='Day of week', enabled=False,
                  choices={'Monday':0, 'Tuesday':1, 'Wednesday':2, 'Thursday':3 ,'Friday':4, 'Saturday':5, 'Sunday':6})
  SYCLCLWD  = MVCField(MVCTypeList + MVCTypeField, Integer, label='Work day')
  SYCLCLBD  = MVCField(MVCTypeList + MVCTypeField, Integer, label='Bank day')
  SYCLCLPD  = MVCField(MVCTypeList + MVCTypeField, Integer, label='Pay day')

  def synchronizeData(self, mvcsession, fieldName, fieldType):
    '''Synchronize data retrieved from user input'''
    fields = mvcsession.entryDataset.FieldsAsDict()
    if fields['SYCLCLDT']:
      cldate = dt.date.today().frominteger(fields['SYCLCLDT'])
      fields['SYCLCLYR'] = cldate.year
      fields['SYCLCLMT'] = cldate.month
      fields['SYCLCLDW'] = cldate.weekday()

      mvcsession.entryDataset.Edit()
      mvcsession.entryDataset.SetFieldValues(fields)
      mvcsession.entryDataset.Post()

    return mvcsession

  def initializeParam(self, mvcsession, query):
    '''Initialize parameters'''
    params = mvcsession.paramDataset.FieldsAsDict()
    proxy = self.getBusinessObjectProxy()
    if params['SYCLCONO'] is None:
      usrobj = proxy.getObject('USROBJ')
      infodict = usrobj.retrieveUserInfoDict(mvcsession)
      params['SYCLCONO'] = infodict['USRCONO']

    cmpobj = proxy.getObject('CMPOBJ')
    cmpobj.validateCompany(params['SYCLCONO'])

    today = dt.date.today()
    if params['SYCLCLMT'] is None:
      params['SYCLCLMT'] = today.month
    if params['SYCLCLYR'] is None:
      params['SYCLCLYR'] = today.year

    mvcsession.paramDataset.Edit()
    mvcsession.paramDataset.SetFieldValues(params)
    mvcsession.paramDataset.Post()

    query = query.filter_by(SYCLCONO = params['SYCLCONO'])
    query = query.filter_by(SYCLCLYR = params['SYCLCLYR'])
    query = query.filter_by(SYCLCLMT = params['SYCLCLMT'])

    return query

  def initializeData(self, mvcsession):
    '''Initializing data'''
    params = mvcsession.paramDataset.FieldsAsDict()
    today = dt.date.today()
    nval = 1 if today.weekday() < 6 else 0
    mvcsession.entryDataset.Append()
    mvcsession.entryDataset.SetFieldValues(params)
    mvcsession.entryDataset.SetFieldValue('SYCLCLDT', today.tointeger())
    mvcsession.entryDataset.SetFieldValue('SYCLCLYR', today.year)
    mvcsession.entryDataset.SetFieldValue('SYCLCLMT', today.month)
    mvcsession.entryDataset.SetFieldValue('SYCLCLDW', today.weekday())
    mvcsession.entryDataset.SetFieldValue('SYCLCLWD', nval)
    mvcsession.entryDataset.SetFieldValue('SYCLCLBD', nval)
    mvcsession.entryDataset.SetFieldValue('SYCLCLPD', nval)
    mvcsession.entryDataset.Post()
    return mvcsession

  def validateData(self, mvcsession):
    '''Validate date retrieved from user input before storing it into persistent storage'''
    fields = mvcsession.entryDataset.FieldsAsDict()

    if fields['SYCLCLDT']:
      cldate = dt.date.today().frominteger(fields['SYCLCLDT'])
      fields['SYCLCLYR'] = cldate.year
      fields['SYCLCLMT'] = cldate.month
      fields['SYCLCLDW'] = cldate.weekday()

      mvcsession.entryDataset.Edit()
      mvcsession.entryDataset.SetFieldValues(fields)
      mvcsession.entryDataset.Post()

    return mvcsession






