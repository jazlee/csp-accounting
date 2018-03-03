"""
Currency Rate, this module purposed for maintain currency rate type reference
linked from currency module which will be needed by various modules on this
system.
"""
__author__    = 'Jaimy Azle'
__version__   = '1.0'
__copyright__ = 'Copyright (c) 2008 Jaimy Azle'

from mvcsvc import *
from elixir import *
import datetime as dt
import sqlalchemy as sa
from validators import *
from tbl import MSTCRT

class CMN045(MVCController):
  """
  Currency Rate, this module purposed for maintain currency rate type reference
  linked from currency module which will be needed by various modules on this
  system.
  """

  _description = 'Currency Rate Type'
  _supported_functions = (MVCFuncSelect, MVCFuncNew, MVCFuncOpen, MVCFuncShow, MVCFuncDelete)
  _model_binder = MVCModelBinder(MSTCRT)

  CMCTCONO  = MVCField(MVCTypeList + MVCTypeField + MVCTypeParam, String(3), label='Curr. Code', enabled=False, visible=False)
  CMCTCUCD  = MVCField(MVCTypeList + MVCTypeField + MVCTypeParam, String(3), label='Curr. Code', charcase=ecUpperCase, browseable=True)
  CMCTTPCD  = MVCField(MVCTypeList + MVCTypeField + MVCTypeParam, String(3), label='Rate Type', charcase=ecUpperCase, browseable=True)
  CMCTCRNM  = MVCField(MVCTypeList + MVCTypeField, String(16), label='Description')
  CMCTDTMT  = MVCField(MVCTypeField, String(1), label='Date Match', choices={'< - Earlier':'<', '= - Exact':'=', '> - Later':'>'})
  CMCTRTOP  = MVCField(MVCTypeField, String(1), label='Rate Operation', choices={'* - Multiply':'*', '/ - Divide':'/'})
  CMCTSRRT  = MVCField(MVCTypeField, String(48), label='Source Rate')

  def initView(self, mvcsession):
    mvcsession.selectFunction = MVCExtFunction('xxx', 'CMN046',
      params = {'CRRTCUCD':'%f:CMCTCUCD',
                'CRRTTPCD':'%f:CMCTTPCD',
                'CRRTSRCP':'%v:'},
      autoSelect=False)
    mvcsession.extFunctions = (
        MVCExtFunction('Currency Rates', 'CMN046',
          params = {'CRRTCUCD':'%f:CMCTCUCD',
                    'CRRTTPCD':'%f:CMCTTPCD',
                    'CRRTSRCP':'%v:'}),
      )
    return mvcsession

  def lookupView(self, session, fieldName):
    ret = MVCLookupDef('','')
    if fieldName == 'CMCTCUCD':
      ret.svcname = 'CMN040'
      ret.retfield = 'CMCRCUCD'
    if fieldName == 'CMCTTPCD':
      ret.svcname = 'CMN050'
      ret.retfield = 'CMRTTPCD'
    return ret

  def initializeParam(self, mvcsession, query):
    '''Initialize parameters'''
    params = mvcsession.paramDataset.FieldsAsDict()
    proxy = self.getBusinessObjectProxy()
    if (params['CMCTCUCD'] in (None, '')) and \
       (params['CMCTTPCD'] in (None, '')):
      raise Exception('Program CMN045 could not be load directly by user')
    if params['CMCTCONO'] in (None, ''):
      usrobj = proxy.getObject('USROBJ')
      usrinfo = usrobj.retrieveUserInfoDict(mvcsession)
      params['CMCTCONO'] = usrinfo['USRCONO']
      mvcsession.paramDataset.Edit()
      mvcsession.paramDataset.SetFieldValues(params)
      mvcsession.paramDataset.Post()

    cmpobj = proxy.getObject('CMPOBJ')
    cmpobj.validateCompany(params['CMCTCONO'])

    query = query.filter_by(CMCTCONO = params['CMCTCONO'])
    if params['CMCTCUCD'] not in (None, ''):
      query = query.filter_by(CMCTCUCD = params['CMCTCUCD'])
    if params['CMCTTPCD'] not in (None, ''):
      query = query.filter_by(CMCTTPCD = params['CMCTTPCD'])
    query = query.order_by(sa.asc(MSTCRT.CMCTCUCD))
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
    validators.NotEmpty(messages={'empty': 'Currency code must not empty'}).to_python(fields['CMCTCUCD'])
    validators.NotEmpty(messages={'empty': 'Rate type code must not empty'}).to_python(fields['CMCTTPCD'])
    return mvcsession


