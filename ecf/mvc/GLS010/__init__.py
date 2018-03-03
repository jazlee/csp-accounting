"""
G/L Account Cluster Definition
"""

__author__    = 'Jaimy Azle'
__version__   = '1.0'
__copyright__ = 'Copyright (c) 2008 Jaimy Azle'

from mvcsvc import *
from elixir import *
import datetime as dt
from validators import *
import sqlalchemy as sa
from tbl import GLSCST

class GLS010(MVCController):
  """
  G/L Account Cluster Defition
  """

  _description = 'Account Cluster Definition'
  _supported_functions = (MVCFuncSelect, MVCFuncNew, MVCFuncOpen, MVCFuncShow, MVCFuncCopy, MVCFuncDelete)
  _model_binder = MVCModelBinder(GLSCST)

  CSCPCSID  = MVCField(MVCTypeList + MVCTypeField, Integer(), label='Cluster ID',
    choices={'01':1, '02':2, '03':3, '04':4, '05':5, '06':6, '07':7, '08':8, '09':9, '10':10})
  CSCPCSNM  = MVCField(MVCTypeList + MVCTypeField, String(32), label='Name')
  CSCPCSLN  = MVCField(MVCTypeList + MVCTypeField, Integer(), label='Length')
  CSCPCSCL  = MVCField(MVCTypeList + MVCTypeField, Integer(), label='Use in closing')

  def initView(self, mvcsession):
    mvcsession.selectFunction = MVCExtFunction('xxx', 'GLS020', params = {'CSSICSID':'%f:CSCPCSID'}, autoSelect=False)
    mvcsession.extFunctions = ( MVCExtFunction('Cluster Identification', 'GLS020', params = {'CSSICSID':'%f:CSCPCSID'}), )
    return mvcsession

  def initializeData(self, mvcsession):
    '''Initializing data'''
    proxy = self.getBusinessObjectProxy()
    mvcsession.entryDataset.Append()
    mvcsession.entryDataset.SetFieldValue('CSCPCSCL', 0)
    mvcsession.entryDataset.Post()
    return mvcsession

  def validateData(self, mvcsession):
    '''Validate data retrieved from user input before storing it into persistent storage'''
    fields = mvcsession.entryDataset.FieldsAsDict()
    validators.NotEmpty(messages={'empty': 'Cluster id must not empty'}).to_python(fields['CSCPCSID'])
    validators.NotEmpty(messages={'empty': 'Cluster name must not empty'}).to_python(fields['CSCPCSNM'])
    return mvcsession

