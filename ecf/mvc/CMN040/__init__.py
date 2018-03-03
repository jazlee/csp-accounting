"""
Currencies, this module purposed for maintain currency list reference needed
by various modules on this system.
"""
__author__    = 'Jaimy Azle'
__version__   = '1.0'
__copyright__ = 'Copyright (c) 2008 Jaimy Azle'

from mvcsvc import *
from elixir import *
from tbl import MSTCUR

class CMN040(MVCController):
  """
  Currencies, this module purposed for maintain currency list reference needed
  by various modules on this system.
  """

  _description = 'Currencies'
  _supported_functions = (MVCFuncNew, MVCFuncOpen, MVCFuncShow, MVCFuncDelete)
  _model_binder = MVCModelBinder(MSTCUR)

  CMCRCUCD  = MVCField(MVCTypeList + MVCTypeField, String(3), label='Curr. Code', charcase=ecUpperCase)
  CMCRCUNM  = MVCField(MVCTypeList + MVCTypeField, String(16), label='Name', synchronized=True)
  CMCRCUDS  = MVCField(MVCTypeList + MVCTypeField, String(32), label='Description')

  def initView(self, mvcsession):
    mvcsession.selectFunction = MVCExtFunction('xxx', 'CMN045', params = {'CMCTCUCD':'%f:CMCRCUCD'}, autoSelect=False)
    mvcsession.extFunctions = [ MVCExtFunction('Currency rate type', 'CMN045', params = {'CMCTCUCD':'%f:CMCRCUCD'}),
      MVCExtFunction('Exchange rate type', 'CMN050')]
    return mvcsession

  def synchronizeData(self, mvcsession, fieldName, fieldType):
    '''Synchronize data retrieved from user input'''
    fields = mvcsession.entryDataset.FieldsAsDict()
    if (fieldName == 'CMCRCUNM') and \
       (fields['CMCRCUNM'] not in ('', None)) and \
       (fields['CMCRCUDS'] in ('', None)):
      mvcsession.entryDataset.Edit()
      mvcsession.entryDataset.SetFieldValue('CMCRCUDS', fields['CMCRCUNM'])
      mvcsession.entryDataset.Post()
    return mvcsession