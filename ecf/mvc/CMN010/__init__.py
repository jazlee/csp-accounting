from mvcsvc import *
from elixir import *
from tbl import MSTCTR

class CMN010(MVCController):
  """
  Countries, this module purposed for maintain country list reference needed
  by various modules on this system.
  """

  _description = 'Countries'
  _supported_functions = (MVCFuncNew, MVCFuncOpen, MVCFuncShow, MVCFuncDelete)
  _model_binder = MVCModelBinder(MSTCTR)

  CMCTIDCD  = MVCField(MVCTypeList + MVCTypeField, String(2), label='Country', charcase=ecUpperCase)
  CMCTIDNM  = MVCField(MVCTypeList + MVCTypeField, String(32), label='Name', synchronized=True)
  CMCTIDDS  = MVCField(MVCTypeList + MVCTypeField, String(48), label='Description')

  def synchronizeData(self, mvcsession, fieldName, fieldType):
    '''Synchronize data retrieved from user input'''
    fields = mvcsession.entryDataset.FieldsAsDict()
    if (fieldName == 'CMCTIDNM') and \
       (fields['CMCTIDNM'] not in ('', None)) and \
       (fields['CMCTIDDS'] in ('', None)):
      mvcsession.entryDataset.Edit()
      mvcsession.entryDataset.SetFieldValue('CMCTIDDS', fields['CMCTIDNM'])
      mvcsession.entryDataset.Post()
    return mvcsession






