"""
G/L Account Structure
"""

__author__    = 'Jaimy Azle'
__version__   = '1.0'
__copyright__ = 'Copyright (c) 2008 Jaimy Azle'

from mvcsvc import *
from elixir import *
import datetime as dt
from validators import *
import sqlalchemy as sa
from tbl import GLSACS

class GLS030(MVCController):
  """
  G/L Account Structure
  """
  _description = 'Account Structure'
  _supported_functions = (MVCFuncSelect, MVCFuncNew, MVCFuncOpen, MVCFuncShow, MVCFuncCopy, MVCFuncDelete)
  _model_binder = MVCModelBinder(GLSACS)

  ACASACCD  = MVCField(MVCTypeList + MVCTypeField, String(8), label='Structure Code', charcase=ecUpperCase)
  ACASACNM  = MVCField(MVCTypeList + MVCTypeField, String(32), label='Name')

  def initView(self, mvcsession):
    mvcsession.selectFunction = MVCExtFunction('xxx', 'GLS031', params = {'AIASACCD':'%f:ACASACCD'}, autoSelect=False)
    mvcsession.extFunctions = (
        MVCExtFunction('Detail Account Structure', 'GLS031', params = {'AIASACCD':'%f:ACASACCD'}),
        MVCExtFunction('Account Cluster Definition', 'GLS010'),
        MVCExtFunction('Cluster Identification', 'GLS020')
      )
    return mvcsession

  def validateData(self, mvcsession):
    '''Validate data retrieved from user input before storing it into persistent storage'''
    fields = mvcsession.entryDataset.FieldsAsDict()
    validators.NotEmpty(messages={'empty': 'Structure code must not empty'}).to_python(fields['ACASACCD'])
    validators.NotEmpty(messages={'empty': 'Structure name must not empty'}).to_python(fields['ACASACNM'])
    return mvcsession

