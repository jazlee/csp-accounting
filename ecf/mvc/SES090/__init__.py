"""
Language
"""

__author__    = 'Jaimy Azle'
__version__   = '1.0'
__copyright__ = 'Copyright (c) 2008 Jaimy Azle'

from mvcsvc import *
from elixir import *
import datetime as dt
from validators import *
import sqlalchemy as sa
import decimal as dcm
from tbl import EFLANG

class SES090(MVCController):
  """
  Language
  """
  _description = 'Language'
  _supported_functions = (MVCFuncSelect, MVCFuncNew, MVCFuncOpen, MVCFuncShow, MVCFuncDelete)
  _model_binder = MVCModelBinder(EFLANG)

  EFLGLCCD  = MVCField(MVCTypeList + MVCTypeField, String(16), charcase=ecUpperCase)
  EFLGLGNM  = MVCField(MVCTypeList + MVCTypeField, String(48), synchronized=True)
  EFLGLGDS  = MVCField(MVCTypeList + MVCTypeField, String(64))

  def synchronizeData(self, mvcsession, fieldName, fieldType):
    if not mvcsession.entryDataset.IsEmpty:
      fields = mvcsession.entryDataset.FieldsAsDict()
      if (fieldName == 'EFLGLGNM') and \
         (fields['EFLGLGNM'] not in (None, '')) and \
         (fields['EFLGLGDS'] in (None, '')):
        mvcsession.entryDataset.Edit()
        mvcsession.entryDataset.SetFieldValue('EFLGLGDS', fields['EFLGLGNM'])
        mvcsession.entryDataset.Post()
    return mvcsession

  def initView(self, mvcsession):
    mvcsession.selectFunction = MVCExtFunction('xxx', 'SES095', \
        params = {
          'EFLCLCCD':'%f:EFLGLCCD',
        }, autoSelect=False
      )
    mvcsession.extFunctions = ( MVCExtFunction('Language translation', 'SES095',
        params = {
          'EFLCLCCD':'%f:EFLGLCCD',
        }),
      )