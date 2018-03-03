"""
G/L Batch List
"""

__author__    = 'Jaimy Azle'
__version__   = '1.0'
__copyright__ = 'Copyright (c) 2008 Jaimy Azle'

from mvcsvc import *
from elixir import *
import datetime as dt
from validators import *
import sqlalchemy as sa
from tbl import GLBCTL, GLBCNO, GLSOPT, GLJHDR, GLJITM, EFUSRS


class GLS100(MVCController):
  """
  G/L Batch List
  """

  _description = 'G/L Batch List'
  _supported_functions = (MVCFuncSelect, MVCFuncNew, MVCFuncOpen, MVCFuncShow, MVCFuncDelete)

  GLBCLSID    = MVCField(MVCTypeList + MVCTypeField, String(6), label='Batch No.', enabled=False)
  GLBCNODS    = MVCField(MVCTypeList + MVCTypeField, String(32), label='Description')
  GLBCSRLG    = MVCField(MVCTypeList + MVCTypeField, String(2), label='Src. Lgr', enabled=False)
  GLBCDTCR    = MVCField(MVCTypeField, Date, label='Created', enabled=False)
  GLBCDTED    = MVCField(MVCTypeList + MVCTypeField, Date, label='Edited', enabled=False)
  GLBCLSTR    = MVCField(MVCTypeField, String(6), label='Last TR ID', enabled=False)
  GLBCCTTR    = MVCField(MVCTypeField, Integer(), label='TR Count', enabled=False)
  GLBCCTER    = MVCField(MVCTypeField, Integer(), label='ERR Count', enabled=False)
  GLBCNTDB    = MVCField(MVCTypeList + MVCTypeField, Numeric(18,4), label='DB Total', enabled=False)
  GLBCNTCR    = MVCField(MVCTypeList + MVCTypeField, Numeric(18,4), label='CR Total', enabled=False)
  GLBCPRST    = MVCField(MVCTypeField, Integer(), label='Printed', enabled=False,
                  choices = {
                    'Yes':1,
                    'No':0})
  GLBCBCTP    = MVCField(MVCTypeField, Integer(), label='Type', enabled=False,
                  choices = {
                    'Subledger':2,
                    'Entered':1})
  GLBCBTP1    = MVCField(MVCTypeList + MVCTypeField, String(12), label='Type', enabled=False,
                  choices = {
                    2:'Subledger',
                    1:'Entered'})
  GLBCBCST    = MVCField(MVCTypeField, Integer(), label='Status', enabled= True,
                  choices={
                    'Open':1,
                    'Ready to post':2,
                    'Posted':3,
                    'Deleted':4,
                    'Error':5
                  })
  GLBCBST1    = MVCField(MVCTypeParam, Integer(), label='Status',
                  choices={
                    'Open':1,
                    'Ready to post':2,
                    'Posted':3,
                    'Deleted':4,
                    'Error':5
                  })
  GLBCPSSQ    = MVCField(MVCTypeField, Integer(), label='Posting Seq', enabled=False)

  def initView(self, mvcsession):
    mvcsession.selectFunction = MVCExtFunction('xxx', 'GLS200', params = {'GLJHBCID':'%f:GLBCLSID'}, autoSelect=False)
    mvcsession.extFunctions = ( MVCExtFunction('Journal Entries', 'GLS200', params = {'GLJHBCID':'%f:GLBCLSID'}), )
    return mvcsession

  def openView(self, mvcsession):
    proxy = self.getBusinessObjectProxy()
    usrobj = proxy.getObject('USROBJ')
    glsobj = proxy.getObject('GLSOBJ')
    info = usrobj.retrieveUserInfoDict(mvcsession)
    cono = info['USRCONO']
    glopt = glsobj.getGLOpt(cono)

    if mvcsession.paramDataset.IsEmpty:
      mvcsession.paramDataset.Append()
      mvcsession.paramDataset.SetFieldValue('GLBCBST1', 1)
      mvcsession.paramDataset.Post()

    q = GLBCTL.query
    q = q.filter_by(GLBCCONO = cono)
    q = q.filter_by(GLBCNOID = glopt['GLOPBCNO'])
    q = q.filter_by(GLBCBCST = mvcsession.paramDataset.GetFieldValue('GLBCBST1'))
    q = q.order_by(sa.asc(GLBCTL.GLBCCONO))
    q = q.order_by(sa.asc(GLBCTL.GLBCNOID))
    objs = q.order_by(sa.desc(GLBCTL.GLBCLSID)).all()

    for obj in objs:
      mvcsession.listDataset.CopyFromORM(
        'GLBCNODS;GLBCSRLG;GLBCDTED;GLBCNTDB;GLBCNTCR',
        'GLBCNODS;GLBCSRLG;GLBCDTED;GLBCNTDB;GLBCNTCR',
        obj
      )
      mvcsession.listDataset.Edit()
      mvcsession.listDataset.SetFieldValue('GLBCLSID', '%.6d' % obj.GLBCLSID)
      mvcsession.listDataset.SetFieldValue('GLBCBTP1', mvcsession.fieldDefs.GLBCBTP1.choices[obj.GLBCBCTP])
      mvcsession.listDataset.Post()

    return mvcsession

  def retrieveData(self, mvcsession):
    proxy = self.getBusinessObjectProxy()
    usrobj = proxy.getObject('USROBJ')
    glsobj = proxy.getObject('GLSOBJ')
    info = usrobj.retrieveUserInfoDict(mvcsession)
    cono = info['USRCONO']
    glopt = glsobj.getGLOpt(cono)
    if (cono in (None, '')):
      raise Exception('Default company for user % is not assigned' % mvcsession.cookies['user_name'].encode('utf8'))
    if mvcsession.execType == MVCExecAppend:
      mvcsession.entryDataset.Append()
      mvcsession.entryDataset.SetFieldValue('GLBCSRLG', 'GL')
      mvcsession.entryDataset.SetFieldValue('GLBCDTCR', dt.date.today().tointeger())
      mvcsession.entryDataset.SetFieldValue('GLBCDTED', dt.date.today().tointeger())
      mvcsession.entryDataset.SetFieldValue('GLBCLSTR', '%.6d' % 0)
      mvcsession.entryDataset.SetFieldValue('GLBCCTTR', 0)
      mvcsession.entryDataset.SetFieldValue('GLBCCTER', 0)
      mvcsession.entryDataset.SetFieldValue('GLBCNTDB', 0)
      mvcsession.entryDataset.SetFieldValue('GLBCNTCR', 0)
      mvcsession.entryDataset.SetFieldValue('GLBCPRST', 0)
      mvcsession.entryDataset.SetFieldValue('GLBCBCTP', 1)
      mvcsession.entryDataset.SetFieldValue('GLBCBCST', 1)
      mvcsession.entryDataset.SetFieldValue('GLBCPSSQ', 0)
      mvcsession.entryDataset.Post()

    if mvcsession.execType in (MVCExecShow, MVCExecEdit, MVCExecDelete, MVCExecCopy):
      lists = mvcsession.listDataset.FieldsAsDict()
      q = GLBCTL.query
      q = q.filter_by(GLBCCONO = cono)
      q = q.filter_by(GLBCNOID = glopt['GLOPBCNO'])
      q = q.filter_by(GLBCLSID = int(lists['GLBCLSID']))
      obj = q.first()
      if mvcsession.execType <> MVCExecCopy:
        if mvcsession.execType == MVCExecDelete:
          if obj.GLBCBCST == 3:
            raise Exception('Cannot delete batch that has already posted')
        mvcsession.entryDataset.CopyFromORM(
          'GLBCNODS;GLBCSRLG;GLBCDTCR;GLBCDTED;GLBCCTTR;GLBCCTER;GLBCNTDB;'\
          'GLBCNTCR;GLBCPRST;GLBCBCTP;GLBCBCST;GLBCPSSQ',
          'GLBCNODS;GLBCSRLG;GLBCDTCR;GLBCDTED;GLBCCTTR;GLBCCTER;GLBCNTDB;'\
          'GLBCNTCR;GLBCPRST;GLBCBCTP;GLBCBCST;GLBCPSSQ',
          obj
        )
        mvcsession.entryDataset.Edit()
        mvcsession.entryDataset.SetFieldValue('GLBCLSID', '%.6d' % obj.GLBCLSID)
        mvcsession.entryDataset.SetFieldValue('GLBCLSTR', '%.6d' % obj.GLBCLSTR)
        mvcsession.entryDataset.Post()

        if mvcsession.execType == MVCExecEdit:
          mvcsession.fieldDefs.GLBCLSID.enabled = False
      else:
        mvcsession.entryDataset.CopyFromORM(
          'GLBCNODS',
          'GLBCNODS',
          obj
        )
        mvcsession.entryDataset.Edit()
        mvcsession.entryDataset.SetFieldValue('GLBCSRLG', 'GL')
        mvcsession.entryDataset.SetFieldValue('GLBCDTCR', dt.date.today().tointeger())
        mvcsession.entryDataset.SetFieldValue('GLBCDTED', dt.date.today().tointeger())
        mvcsession.entryDataset.SetFieldValue('GLBCLSTR', '%.6d' % 0)
        mvcsession.entryDataset.SetFieldValue('GLBCCTTR', 0)
        mvcsession.entryDataset.SetFieldValue('GLBCCTER', 0)
        mvcsession.entryDataset.SetFieldValue('GLBCNTDB', 0)
        mvcsession.entryDataset.SetFieldValue('GLBCNTCR', 0)
        mvcsession.entryDataset.SetFieldValue('GLBCPRST', 0)
        mvcsession.entryDataset.SetFieldValue('GLBCBCTP', 1)
        mvcsession.entryDataset.SetFieldValue('GLBCBCST', 1)
        mvcsession.entryDataset.SetFieldValue('GLBCPSSQ', 0)
        mvcsession.entryDataset.Post()
    return mvcsession

  def postData(self, mvcsession):
    proxy = self.getBusinessObjectProxy()
    usrobj = proxy.getObject('USROBJ')
    glsobj = proxy.getObject('GLSOBJ')
    info = usrobj.retrieveUserInfoDict(mvcsession)
    cono = info['USRCONO']
    glopt = glsobj.getGLOpt(cono)
    fields = mvcsession.entryDataset.FieldsAsDict()
    validators.NotEmpty(messages={'empty': 'Description must not empty'}).to_python(fields['GLBCNODS'])
    td = dt.datetime.now()

    if mvcsession.execType in (MVCExecAppend, MVCExecCopy):
      if fields['GLBCBCST'] != 1:
        raise Exception('only OPEN status accepted for new batch')
      lsno = GLBCNO.getLSNO(glopt['GLOPBCNO'])
      obj = GLBCTL(
          GLBCCONO  = cono,
          GLBCNOID  = glopt['GLOPBCNO'],
          GLBCLSID  = lsno,
          GLBCNODS  = fields['GLBCNODS'],
          GLBCLSTR  = 0,
          GLBCCTTR  = 0,
          GLBCCTER  = 0,
          GLBCNTDB  = 0,
          GLBCNTCR  = 0,
          GLBCPRST  = 0,
          GLBCDTCR  = td.date().tointeger(),
          GLBCDTED  = td.date().tointeger(),
          GLBCSRLG  = fields['GLBCSRLG'],
          GLBCBCTP  = fields['GLBCBCTP'],
          GLBCBCST  = fields['GLBCBCST'],
          GLBCPSSQ  = 0,
          GLBCAUDT  = td.date().tointeger(),
          GLBCAUTM  = td.time().tointeger(),
          GLBCAUUS  = mvcsession.cookies['user_name'].encode('utf8')
        )
      if not session.transaction_started():
        session.begin()
      try:
        session.save(obj)
        session.commit()
      except:
        session.rollback()
        session.expunge(obj)
        raise
    if (mvcsession.execType in (MVCExecEdit, MVCExecDelete)):
      obj = GLBCTL.getObj(False, GLBCCONO = cono, GLBCNOID = glopt['GLOPBCNO'], GLBCLSID = fields['GLBCLSID'])
      if not obj:
        raise Exception('Record could not be found')
      if (mvcsession.execType == MVCExecEdit):
        if (obj.GLBCBCST != fields['GLBCBCST']):
          if fields['GLBCBCST'] not in (1, 2, 5):
            raise Exception('Modified batch status is not accepted')
          if fields['GLBCBCST'] in (1, 2, 5) and (obj.GLBCBCST in (3, 4)):
            raise Exception('Modified batch status is not accepted')
          if (fields['GLBCBCST'] == 5) and (obj.GLBCBCST != fields['GLBCBCST']):
            raise Exception('Only system could mark batch status as ERROR')
        obj.GLBCNODS = fields['GLBCNODS']
        if (obj.GLBCBCST != fields['GLBCBCST']):
          obj.GLBCBCST = fields['GLBCBCST']
        obj.GLBCDTED = td.date().tointeger()
        obj.GLBCAUDT = td.date().tointeger()
        obj.GLBCAUTM = td.time().tointeger()
        obj.GLBCAUUS = mvcsession.cookies['user_name'].encode('utf8')
        if not session.transaction_started():
          session.begin()
        try:
          session.update(obj)
          session.commit()
        except:
          session.rollback()
          session.expunge(obj)
          raise
      if (mvcsession.execType == MVCExecDelete):
        if obj.GLBCBCST == 3:
          raise Exception('Cannot delete batch that has already posted')

        aadjust = False
        if obj.GLBCBCST != 4:
          aadjust = True
        if not session.transaction_started():
          session.begin()
        try:
          if aadjust == True:
            obj.GLBCBCST = 4
            session.update(obj)
          else:
            hdrs = GLJHDR.getObj(True, GLJHCONO = obj.GLBCCONO, GLJHNOID = obj.GLBCNOID, \
              GLJHBCID = obj.GLBCLSID)
            for hdr in hdrs:
              itms = GLJITM.getObj(True, GLJICONO = hdr.GLJHCONO, GLJINOID = hdr.GLJHNOID, \
                GLJIBCID = hdr.GLJHBCID, GLJIJEID = hdr.GLJHJEID)
              if not session.transaction_started():
                session.begin()
              session.delete(hdr)
              session.commit()
              for itm in itms:
                session.delete(itm)
            session.delete(obj)
          session.commit()
        except:
          session.clear()
          session.rollback()
          raise
    return mvcsession



