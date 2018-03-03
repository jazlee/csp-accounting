"""
Translation
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
from tbl import EFLANG, EFLOCL

class SES095(MVCController):
  """
  Translation
  """
  _description = 'Translation'
  _supported_functions = (MVCFuncNew, MVCFuncOpen, MVCFuncShow, MVCFuncDelete)
  _model_binder = MVCModelBinder(EFLOCL)

  EFLCLCCD  = MVCField(MVCTypeParam + MVCTypeList + MVCTypeField, String(16), browseable=True, charcase=ecUpperCase, synchronized=True)
  EFLCMDTP  = MVCField(MVCTypeParam + MVCTypeField, Integer, label='Module type', choices={
                    'Module':1,
                    'API':2
                })
  EPLCMDCD  = MVCField(MVCTypeParam, String(32), label='Module', browseable=True, charcase=ecUpperCase, synchronized=True)
  EFLCMDCD  = MVCField(MVCTypeList + MVCTypeField, String(32), browseable=True, charcase=ecUpperCase, synchronized=True)
  EFLCMSID  = MVCField(MVCTypeList + MVCTypeField, String(64), synchronized=True)
  EFLCMSLS  = MVCField(MVCTypeList + MVCTypeField, String(250))

  def generateTranslation(self, mvcsession):
    '''Generate initial translation'''
    params = mvcsession.paramDataset.FieldsAsDict()
    proxy = self.getBusinessObjectProxy()
    locobj = proxy.getObject('CMNOBJ')
    locobj.generateInitialTranslation(mvcsession, params['EFLCLCCD'], params['EPLCMDCD'], params['EFLCMDTP'])
    return mvcsession

  def initView(self, mvcsession):
    '''Initialize the program'''
    mvcsession.extFunctions = (
        MVCExtFunction('Generate initial translation', self.generateTranslation),
      )
    return mvcsession

  def synchronizeData(self, mvcsession, fieldName, fieldType):
    if not mvcsession.entryDataset.IsEmpty:
      fields = mvcsession.entryDataset.FieldsAsDict()
      if (fieldName == 'EFLCMSID') and \
         (fields['EFLCMSID'] not in (None, '')) and \
         (fields['EFLCMSLS'] in (None, '')):
        mvcsession.entryDataset.Edit()
        mvcsession.entryDataset.SetFieldValue('EFLCMSLS', fields['EFLCMSID'])
        mvcsession.entryDataset.Post()
    return mvcsession

  def initializeParam(self, mvcsession, query):
    if (mvcsession.paramDataset.RecordCount == 0):
      mvcsession.paramDataset.Append()
      mvcsession.paramDataset.SetFieldValue('EFLCMDTP', 1)
      mvcsession.paramDataset.Post()
    else:
      fields = mvcsession.paramDataset.FieldsAsDict()
      if fields['EFLCMDTP'] in (None, 0):
        mvcsession.paramDataset.Edit()
        mvcsession.paramDataset.SetFieldValue('EFLCMDTP', 1)
        mvcsession.paramDataset.Post()
    fields = mvcsession.paramDataset.FieldsAsDict()
    query = query.filter_by(EFLCLCCD = fields['EFLCLCCD'])
    query = query.filter_by(EFLCMDCD = fields['EPLCMDCD'])
    return query

  def lookupView(self, mvcsession, fieldName):
    ret = MVCLookupDef('','')
    if fieldName in ('EFLCLCCD', 'EPLCMDCD', 'EFLCMDCD'):
      if fieldName == 'EFLCLCCD':
        ret.svcname = 'SES090'
        ret.retfield = 'EFLGLCCD'

      if fieldName == 'EPLCMDCD':
        fields = mvcsession.paramDataset.FieldsAsDict()
        if (fields['EFLCMDTP'] == 1):
          ret.svcname = 'SES020'
          ret.retfield = 'EFMVCONM'
        elif (fields['EFLCMDTP'] == 2):
          ret.svcname = 'SES030'
          ret.retfield = 'EFAPIONM'

      if fieldName == 'EFLCMDCD':
        fields = mvcsession.entryDataset.FieldsAsDict()
        if (fields['EFLCMDTP'] == 1):
          ret.svcname = 'SES020'
          ret.retfield = 'EFMVCONM'
        elif (fields['EFLCMDTP'] == 2):
          ret.svcname = 'SES030'
          ret.retfield = 'EFAPIONM'
    return ret

  def initializeData(self, mvcsession):
    if mvcsession.execType == MVCExecAppend:
      fields = mvcsession.paramDataset.FieldsAsDict()
      mvcsession.entryDataset.Append()
      mvcsession.entryDataset.SetFieldValue('EFLCMDTP', fields['EFLCMDTP'])
      mvcsession.entryDataset.SetFieldValue('EFLCLCCD', fields['EFLCLCCD'])
      mvcsession.entryDataset.SetFieldValue('EFLCMDCD', fields['EPLCMDCD'])
      mvcsession.entryDataset.Post()
    return mvcsession

  def afterRetrieveData(self, mvcsession, obj):
    if mvcsession.execType == MVCExecEdit:
      mvcsession.fieldDefs.EFLCMDTP.enabled = False;
    return mvcsession, obj