"""
API Method Function List
"""

__author__    = 'Jaimy Azle'
__version__   = '1.0'
__copyright__ = 'Copyright (c) 2008 Jaimy Azle'

from apisvc import *
from mvcsvc import *
from elixir import *
from validators import *

class SES032(MVCController):
  """
  API Method Function List
  """

  _description = 'API Method Function List'
  _active = True
  _supported_functions = (MVCFuncShow,)

  EFAPIONM    = MVCField(MVCTypeParam, String(24), label = 'Service Name', enabled=False)
  EFAPIFNM    = MVCField(MVCTypeParam, String(32), label = 'Method', enabled=False)
  EFAPION1    = MVCField(MVCTypeList, String(24), label = 'Service Name', enabled=False, visible=False)
  EFAPIFN1    = MVCField(MVCTypeList, String(32), label = 'Method', enabled=False, visible=False)
  EFAPILNM    = MVCField(MVCTypeField + MVCTypeList, String(32), label = 'Field Name', enabled=False)
  EFAPILDS    = MVCField(MVCTypeField + MVCTypeList, String(48), label = 'Description', enabled=False)
  EFAPILTP    = MVCField(MVCTypeField + MVCTypeList, String(16), label = 'Type', enabled=False)
  EFAPILSZ    = MVCField(MVCTypeField + MVCTypeList, Integer(), label = 'Size', enabled=False)
  EFAPILPR    = MVCField(MVCTypeField + MVCTypeList, Integer(), label = 'Precision', enabled=False)
  EFAPILDC    = MVCField(MVCTypeField + MVCTypeList, Integer(), label = 'Decimal', enabled=False)
  EFAPILRQ    = MVCField(MVCTypeField + MVCTypeList, String(4), label = 'Required', enabled=False)


  def openView(self, mvcsession):
    stats = {True:'Yes', False:'No'}
    service = APILocalService('__APIPROXY__')
    if mvcsession.paramDataset.RecordCount == 0:
      raise Exception('Program SES032 could not be load directly by user')
    metst = service.methodStatus(mvcsession.paramDataset.GetFieldValue('EFAPIONM'), mvcsession.paramDataset.GetFieldValue('EFAPIFNM'))
    oblst = service.fieldList(mvcsession.paramDataset.GetFieldValue('EFAPIONM'), mvcsession.paramDataset.GetFieldValue('EFAPIFNM'))
    if metst[2] == 'D':
      for (aa, ab, ac, ad, ae, af, ag, ah) in oblst:
        mvcsession.listDataset.Append()
        mvcsession.listDataset.SetFieldValue('EFAPION1', mvcsession.paramDataset.GetFieldValue('EFAPIONM'))
        mvcsession.listDataset.SetFieldValue('EFAPIFN1', mvcsession.paramDataset.GetFieldValue('EFAPIFNM'))
        mvcsession.listDataset.SetFieldValue('EFAPILNM', aa)
        mvcsession.listDataset.SetFieldValue('EFAPILDS', ab)
        mvcsession.listDataset.SetFieldValue('EFAPILTP', ad)
        mvcsession.listDataset.SetFieldValue('EFAPILSZ', ae)
        mvcsession.listDataset.SetFieldValue('EFAPILPR', af)
        mvcsession.listDataset.SetFieldValue('EFAPILDC', ag)
        mvcsession.listDataset.SetFieldValue('EFAPILRQ', stats[ah])
        mvcsession.listDataset.Post()
    else:
      for (aa, ab) in oblst:
        mvcsession.listDataset.Append()
        mvcsession.listDataset.SetFieldValue('EFAPION1', mvcsession.paramDataset.GetFieldValue('EFAPIONM'))
        mvcsession.listDataset.SetFieldValue('EFAPIFN1', mvcsession.paramDataset.GetFieldValue('EFAPIFNM'))
        mvcsession.listDataset.SetFieldValue('EFAPILNM', aa)
        mvcsession.listDataset.SetFieldValue('EFAPILDS', ab)
        mvcsession.listDataset.Post()

    return mvcsession

  def retrieveData(self, mvcsession):
    stats = {True:'Yes', False:'No'}
    fields = mvcsession.listDataset.FieldsAsDict()
    if mvcsession.execType in (MVCExecShow, MVCExecEdit):
      service = APILocalService('__APIPROXY__')
      metst = service.methodStatus(fields['EFAPION1'], fields['EFAPIFN1'])
      oblst = service.fieldStatus(fields['EFAPION1'], fields['EFAPIFN1'], fields['EFAPILNM'])
      if metst[2] == 'D':
        if oblst:
          mvcsession.entryDataset.Append()
          mvcsession.entryDataset.SetFieldValue('EFAPILNM', oblst[0])
          mvcsession.entryDataset.SetFieldValue('EFAPILDS', oblst[1])
          mvcsession.entryDataset.SetFieldValue('EFAPILTP', oblst[3])
          mvcsession.entryDataset.SetFieldValue('EFAPILSZ', oblst[4])
          mvcsession.entryDataset.SetFieldValue('EFAPILPR', oblst[5])
          mvcsession.entryDataset.SetFieldValue('EFAPILDC', oblst[6])
          mvcsession.entryDataset.SetFieldValue('EFAPILRQ', stats[oblst[7]])
          mvcsession.entryDataset.Post()
      else:
        if oblst:
          mvcsession.entryDataset.Append()
          mvcsession.entryDataset.SetFieldValue('EFAPILNM', oblst[0])
          mvcsession.entryDataset.SetFieldValue('EFAPILDS', oblst[1])
          mvcsession.entryDataset.Post()

    return mvcsession



