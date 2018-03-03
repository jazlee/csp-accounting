"""
Currency Rate, this module purposed for maintain currency rate reference linked
from currency and currency rate module which will be needed by various modules
on this system.
"""
__author__    = 'Jaimy Azle'
__version__   = '1.0'
__copyright__ = 'Copyright (c) 2008 Jaimy Azle'

from mvcsvc import *
from elixir import *
import datetime as dt
import sqlalchemy as sa
from tbl import CURRAT

class CMN046(MVCController):
  """
  Currency Rate, this module purposed for maintain currency rate reference linked
  from currency and currency rate module which will be needed by various modules
  on this system.
  """

  _description = 'Currency Rates'
  _supported_functions = (MVCFuncNew, MVCFuncOpen, MVCFuncShow, MVCFuncDelete)
  _model_binder = MVCModelBinder(CURRAT)

  CRRTCONO  = MVCField(MVCTypeList + MVCTypeField + MVCTypeParam, String(3), label='Comp. ID', enabled=False, visible=False)
  CRRTCUCD  = MVCField(MVCTypeList + MVCTypeField + MVCTypeParam, String(3), label='Curr. Code', enabled=False)
  CRRTTPCD  = MVCField(MVCTypeList + MVCTypeField + MVCTypeParam, String(3), label='Rate Type', enabled=False)
  CRRTSRCP  = MVCField(MVCTypeParam, String(3), label='Source Currency', enabled=False)
  CRRTSRCD  = MVCField(MVCTypeList + MVCTypeField, String(3), label='Source Currency', charcase=ecUpperCase, browseable=True)
  CRRTRTDT  = MVCField(MVCTypeList + MVCTypeField, Date, label='Rate Date')
  CRRTRTVL  = MVCField(MVCTypeList + MVCTypeField, Numeric(15, 4), label='Rate Value')
  CRRTRTSP  = MVCField(MVCTypeList + MVCTypeField, Numeric(15, 4), label='Spread Value')

  def lookupView(self, session, fieldName):
    ret = MVCLookupDef('','')
    if fieldName == 'CRRTSRCD':
      ret.svcname = 'CMN040'
      ret.retfield = 'CMCRCUCD'
    return ret

  def initializeParam(self, mvcsession, query):
    '''Initialize parameters'''
    params = mvcsession.paramDataset.FieldsAsDict()
    proxy = self.getBusinessObjectProxy()
    if (params['CRRTCUCD'] in (None, '')) and \
       (params['CRRTTPCD'] in (None, '')):
      raise Exception('Program CMN046 could not be load directly by user')
    if params['CRRTCONO'] in (None, ''):
      usrobj = proxy.getObject('USROBJ')
      usrinfo = usrobj.retrieveUserInfoDict(mvcsession)
      params['CRRTCONO'] = usrinfo['USRCONO']
      mvcsession.paramDataset.Edit()
      mvcsession.paramDataset.SetFieldValues(params)
      mvcsession.paramDataset.Post()

    cmpobj = proxy.getObject('CMPOBJ')
    cmpobj.validateCompany(params['CRRTCONO'])

    query = query.filter_by(CRRTCONO = params['CRRTCONO'])
    if params['CRRTCUCD'] not in ('', None):
      query = query.filter_by(CRRTCUCD = params['CRRTCUCD'])
    if params['CRRTTPCD'] not in ('', None):
      query = query.filter_by(CRRTTPCD = params['CRRTTPCD'])
    if params['CRRTSRCP'] not in ('', None):
      query = query.filter_by(CRRTSRCD = params['CRRTSRCP'])
    return query

  def initializeData(self, mvcsession):
    '''Initializing data'''
    params = mvcsession.paramDataset.FieldsAsDict()
    mvcsession.entryDataset.Append()
    mvcsession.entryDataset.SetFieldValue('CRRTCONO', params['CRRTCONO'])
    mvcsession.entryDataset.SetFieldValue('CRRTTPCD', params['CRRTTPCD'])
    mvcsession.entryDataset.SetFieldValue('CRRTSRCD', params['CRRTSRCP'])
    mvcsession.entryDataset.SetFieldValue('CRRTCUCD', params['CRRTCUCD'])
    mvcsession.entryDataset.SetFieldValue('CRRTRTDT', dt.date.today().tointeger())
    mvcsession.entryDataset.SetFieldValue('CRRTRTVL', 1)
    mvcsession.entryDataset.Post()
    return mvcsession


