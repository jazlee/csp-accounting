"""
MVC Program List
"""

__author__    = 'Jaimy Azle'
__version__   = '1.0'
__copyright__ = 'Copyright (c) 2008 Jaimy Azle'

from mvcsvc import *
from elixir import *
from validators import *

class SES020(MVCController):
  """
  MVC Program List
  """
  _description = 'MVC Program List'
  _active = True
  _supported_functions = (MVCFuncShow,)

  EFMVCONM    = MVCField(MVCTypeField + MVCTypeList, String(24), label = 'Service Name', enabled=False)
  EFMVCODS    = MVCField(MVCTypeField + MVCTypeList, String(64), label = 'Description', enabled=False)
  EFMVCOST    = MVCField(MVCTypeField + MVCTypeList, String(8), label = 'Status', enabled=False)

  def openView(self, mvcsession):
    stats = {True:'Active', False:'Inactive'}
    service = MVCLocalService('__MVCPROXY__')
    oblst = service.objectList()
    oblst = sorted(oblst, key=lambda i: i[0])
    for (obnm, obds, obst) in oblst:
      mvcsession.listDataset.Append()
      mvcsession.listDataset.SetFieldValue('EFMVCONM', obnm)
      mvcsession.listDataset.SetFieldValue('EFMVCODS', obds)
      mvcsession.listDataset.SetFieldValue('EFMVCOST', stats[obst])
      mvcsession.listDataset.Post()
    return mvcsession

  def retrieveData(self, mvcsession):
    stats = {True:'Active', False:'Inactive'}
    fields = mvcsession.listDataset.FieldsAsDict()
    if mvcsession.execType in (MVCExecShow, MVCExecEdit):
      service = MVCLocalService('__MVCPROXY__')
      oblst = service.objectStatus(fields['EFMVCONM'])
      if oblst:
        mvcsession.entryDataset.Append()
        mvcsession.entryDataset.SetFieldValue('EFMVCONM', oblst[0])
        mvcsession.entryDataset.SetFieldValue('EFMVCODS', oblst[1])
        mvcsession.entryDataset.SetFieldValue('EFMVCOST', stats[oblst[2]])
        mvcsession.entryDataset.Post()
    return mvcsession



