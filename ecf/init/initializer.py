import procsvc
from tbl import EFUSRS, EFUAOB, EFUAFN, EFUMOB, EFUGRP

def doInitProc():
  objectList = ['USROBJ', 'CMNOBJ', 'CUROBJ', 'CMPOBJ', 'SYSOBJ']

  proxy = procsvc.getBOProxy()
  for obj in objectList:
    objmod = proxy.getObject(obj)
    objmod.initDatabase()


