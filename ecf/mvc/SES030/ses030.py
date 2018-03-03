"""
API Program List
"""

__author__    = 'Jaimy Azle'
__version__   = '1.0'
__copyright__ = 'Copyright (c) 2008 Jaimy Azle'

from apisvc import *
from mvcsvc import *
from elixir import *
from validators import *

class SES030(MVCController):
  """
  API Program List
  """

  _description = 'API Program List'
  _active = True
  _supported_functions = (MVCFuncSelect, MVCFuncShow)

  EFAPIONM    = MVCField(MVCTypeField + MVCTypeList, String(24), label = 'Service Name', enabled=False)
  EFAPIODS    = MVCField(MVCTypeField + MVCTypeList, String(64), label = 'Description', enabled=False)
  EFAPIOST    = MVCField(MVCTypeField + MVCTypeList, String(8), label = 'Status', enabled=False)

  def initView(self, mvcsession):
    mvcsession.extFunctions = (
      MVCExtFunction('Open API Functions list', 'SES031', params = {'EFAPIONM':'%f:EFAPIONM', 'EFAPIODS':'%f:EFAPIODS'}),
      )
    mvcsession.selectFunction = MVCExtFunction('Open API Functions list', 'SES031', params = {'EFAPIONM':'%f:EFAPIONM', 'EFAPIODS':'%f:EFAPIODS'}, autoSelect=True)
    return mvcsession

  def openView(self, mvcsession):
    stats = {True:'Active', False:'Inactive'}
    service = APILocalService('__APIPROXY__')
    oblst = service.objectList()
    oblst = sorted(oblst, key=lambda i: i[0])
    for (obnm, obds, obst) in oblst:
      mvcsession.listDataset.Append()
      mvcsession.listDataset.SetFieldValue('EFAPIONM', obnm)
      mvcsession.listDataset.SetFieldValue('EFAPIODS', obds)
      mvcsession.listDataset.SetFieldValue('EFAPIOST', stats[obst])
      mvcsession.listDataset.Post()
    return mvcsession

  def retrieveData(self, mvcsession):
    stats = {True:'Active', False:'Inactive'}
    if mvcsession.execType in (MVCExecShow, MVCExecEdit):
      service = APILocalService('__APIPROXY__')
      oblst = service.objectStatus(mvcsession.listDataset.GetFieldValue('EFAPIONM'))
      if oblst:
        mvcsession.entryDataset.Append()
        mvcsession.entryDataset.SetFieldValue('EFAPIONM', oblst[0])
        mvcsession.entryDataset.SetFieldValue('EFAPIODS', oblst[1])
        mvcsession.entryDataset.SetFieldValue('EFAPIOST', stats[oblst[2]])
        mvcsession.entryDataset.Post()
    return mvcsession



