"""
API Method List
"""

__author__    = 'Jaimy Azle'
__version__   = '1.0'
__copyright__ = 'Copyright (c) 2008 Jaimy Azle'

from apisvc import *
from mvcsvc import *
from elixir import *
from validators import *

class SES031(MVCController):
  """
  API Method List
  """

  _description = 'API Method List'
  _active = True
  _supported_functions = (MVCFuncSelect, MVCFuncShow)

  EFAPIONM    = MVCField(MVCTypeParam, String(24), label = 'Service Name', enabled=False)
  EFAPIODS    = MVCField(MVCTypeParam, String(64), label = 'Description', enabled=False)
  EFAPION1    = MVCField(MVCTypeList, String(24), label = 'Service Name', enabled=False, visible=False)
  EFAPIFNM    = MVCField(MVCTypeField + MVCTypeList, String(32), label = 'Method', enabled=False)
  EFAPIFDS    = MVCField(MVCTypeField + MVCTypeList, String(64), label = 'Description', enabled=False)
  EFAPIFTP    = MVCField(MVCTypeField + MVCTypeList, String(4), label = 'Type', enabled=False)
  EFAPIFAB    = MVCField(MVCTypeField + MVCTypeList, String(8), label = 'Capability', enabled=False)
  EFAPIFST    = MVCField(MVCTypeField + MVCTypeList, String(8), label = 'Status', enabled=False)

  def initView(self, mvcsession):
    mvcsession.extFunctions = (
      MVCExtFunction('Open functions field list', 'SES032', params = {'EFAPIONM':'%f:EFAPION1', 'EFAPIFNM':'%f:EFAPIFNM'}),
      )
    mvcsession.selectFunction = MVCExtFunction('Open functions field list', 'SES032', params = {'EFAPIONM':'%f:EFAPION1', 'EFAPIFNM':'%f:EFAPIFNM'})
    return mvcsession

  def openView(self, mvcsession):
    stats = {True:'Active', False:'Inactive'}
    service = APILocalService('__APIPROXY__')
    if mvcsession.paramDataset.RecordCount == 0:
      raise Exception('Program SES031 could not be load directly by user')
    objst = service.objectStatus(mvcsession.paramDataset.GetFieldValue('EFAPIONM'))
    mvcsession.paramDataset.Edit()
    mvcsession.paramDataset.SetFieldValue('EFAPIODS', objst[1])
    mvcsession.paramDataset.Post()
    oblst = service.methodList(mvcsession.paramDataset.GetFieldValue('EFAPIONM'))
    for (mtnm, mtds, mttp, mtst, mtab) in oblst:
      mvcsession.listDataset.Append()
      mvcsession.listDataset.SetFieldValue('EFAPION1', mvcsession.paramDataset.GetFieldValue('EFAPIONM'))
      mvcsession.listDataset.SetFieldValue('EFAPIFNM', mtnm)
      mvcsession.listDataset.SetFieldValue('EFAPIFDS', mtds)
      mvcsession.listDataset.SetFieldValue('EFAPIFTP', mttp)
      mvcsession.listDataset.SetFieldValue('EFAPIFAB', mtab)
      mvcsession.listDataset.SetFieldValue('EFAPIFST', stats[mtst])
      mvcsession.listDataset.Post()
    return mvcsession

  def retrieveData(self, mvcsession):
    stats = {True:'Active', False:'Inactive'}
    if mvcsession.execType in (MVCExecShow, MVCExecEdit):
      service = APILocalService('__APIPROXY__')
      oblst = service.methodStatus(mvcsession.listDataset.GetFieldValue('EFAPION1'), mvcsession.listDataset.GetFieldValue('EFAPIFNM'))
      if oblst:
        mvcsession.entryDataset.Append()
        mvcsession.entryDataset.SetFieldValue('EFAPIFNM', oblst[0])
        mvcsession.entryDataset.SetFieldValue('EFAPIFDS', oblst[1])
        mvcsession.entryDataset.SetFieldValue('EFAPIFTP', oblst[2])
        mvcsession.entryDataset.SetFieldValue('EFAPIFAB', oblst[4])
        mvcsession.entryDataset.SetFieldValue('EFAPIFST', stats[oblst[3]])
        mvcsession.entryDataset.Post()
    return mvcsession



