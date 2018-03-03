"""
G/L Options
"""

__author__    = 'Jaimy Azle'
__version__   = '1.0'
__copyright__ = 'Copyright (c) 2008 Jaimy Azle'

from mvcsvc import *
from elixir import *
import datetime as dt
import sqlalchemy as sa
from validators import *
from tbl import GLSOPT, MSTCMP, GLSACS, GLSCST, EFUSRS, GLACCT

class GLS060(MVCController):
  """
  G/L Options
  """

  _description = 'G/L Options'
  _supported_functions = (MVCFuncNew, MVCFuncOpen, MVCFuncShow)

  GLOPCONO  = MVCField(MVCTypeField, String(3), label='Company', charcase=ecUpperCase, browseable=True, enabled=False)
  GLOPCLCD  = MVCField(MVCTypeField, String(48), label='Closing Acct', browseable=True, synchronized=True)
  GLOPCLNM  = MVCField(MVCTypeField, String(48), label='Acct Name', enabled=False)
  GLOPPVST  = MVCField(MVCTypeField, Integer, label='Allow provisional posting')
  GLOPPRST  = MVCField(MVCTypeField, Integer, label='Allow posting to prev. Year')
  GLOPFSTP  = MVCField(MVCTypeField, String(3), label='Default Fiscal Type', browseable=True, synchronized=True)
  GLOPFSNM  = MVCField(MVCTypeField, String(16), label='Default Fiscal Name', enabled=False)
  GLOPFSYR  = MVCField(MVCTypeField, Integer, label='Default Fiscal Year', browseable=True)
  GLOPACSC  = MVCField(MVCTypeField, String(8), label='Default Structure Code', browseable=True, synchronized=True)
  GLOPSCNM  = MVCField(MVCTypeField, String(32), label='Structure Name', enabled=False)
  GLOPACSG  = MVCField(MVCTypeField, Integer, label='Account Cluster',
    choices={'01':1, '02':2, '03':3, '04':4, '05':5, '06':6, '07':7, '08':8, '09':9, '10':10},
    synchronized=True)
  GLOPSGNM  = MVCField(MVCTypeField, String(32), label='Cluster Name', enabled=False)
  GLOPACDL  = MVCField(MVCTypeField, String(1), label='Account Delimeter',
    choices={'-':'-', '.':'.', ':':':', '/':'/'})
  GLOPBCNO  = MVCField(MVCTypeField, String(3), label='Batch Number Opt.', browseable=True)

  def lookupView(self, session, fieldName):
    ret = MVCLookupDef('','')
    if fieldName == 'GLOPACSC':
      ret.svcname = 'GLS030'
      ret.retfield = 'ACASACCD'

    if fieldName == 'GLOPCLCD':
      ret.svcname = 'GLS450'
      ret.retfield = 'GLACACFM'

    if fieldName == 'GLOPBCNO':
      ret.svcname = 'GLS070'
      ret.retfield = 'GLBCNOID'

    if fieldName == 'GLOPFSTP':
      ret.svcname = 'CMN080'
      ret.params = {'FSTPCONO':'%f:GLOPCONO'}
      ret.retfield = 'FSTPTPCD'

    if fieldName == 'GLOPFSYR':
      ret.svcname = 'CMN090'
      ret.params = {'FSYRCONO': '%f:GLOPCONO',
                    'FSYRTPCD': '%f:GLOPFSTP'}
      ret.retfield = 'FSYRFSYR'
    return ret

  def synchronizeData(self, mvcsession, fieldName, fieldType):
    dataset = mvcsession.entryDataset if fieldType == MVCTypeField else \
      mvcsession.paramDataset
    fields = dataset.FieldsAsDict()
    proxy = self.getBusinessObjectProxy()

    usrobj = proxy.getObject('USROBJ')
    glsobj = proxy.getObject('GLSOBJ')

    usrinfo = usrobj.retrieveUserInfoDict(mvcsession)
    cono = usrinfo['USRCONO']

    if (fieldName == 'GLOPCLCD'):
      if (fields['GLOPCLCD'] in (None, '')):
        raise Exception('Account ID must not empty')

      acct = glsobj.getAcct(cono, fields['GLOPCLCD'])
      if acct['GLACACID'] is None:
        raise Exception('Account ID does not exist')

      mvcsession.entryDataset.Edit()
      mvcsession.entryDataset.SetFieldValue('GLOPCLCD', acct['GLACACFM'])
      mvcsession.entryDataset.SetFieldValue('GLOPCLNM', acct['GLACACNM'])
      mvcsession.entryDataset.Post()

    if (fields['GLOPFSTP'] not in (None, '')):
      fscobj = proxy.getObject('FSCOBJ')
      ret = fscobj.getFiscalType(cono, fields['GLOPFSTP'])
      if ret[0] is None:
        raise Exception('Fiscal type is not defined yet')

      mvcsession.entryDataset.Edit()
      mvcsession.entryDataset.SetFieldValue('GLOPFSNM', \
        ret[2])
      mvcsession.entryDataset.Post()

    if (fields['GLOPACSC'] != None):
      values = glsobj.getAcctStructure(fields['GLOPACSC'])
      mvcsession.entryDataset.Edit()
      mvcsession.entryDataset.SetFieldValue('GLOPSCNM', values['ACASACNM'])
      mvcsession.entryDataset.Post()

    if (fields['GLOPACSG'] != None):
      values = glsobj.getAcctCluster(fields['GLOPACSG'])
      mvcsession.entryDataset.Edit()
      mvcsession.entryDataset.SetFieldValue('GLOPSGNM', values['CSCPCSNM'])
      mvcsession.entryDataset.Post()

    return mvcsession

  def retrieveData(self, mvcsession):
    proxy = self.getBusinessObjectProxy()

    usrobj = proxy.getObject('USROBJ')
    glsobj = proxy.getObject('GLSOBJ')
    fscobj = proxy.getObject('FSCOBJ')

    usrinfo = usrobj.retrieveUserInfoDict(mvcsession)
    cono = usrinfo['USRCONO']

    if cono is None:
      raise Exception('Could not retrieve your information, perhaps it was deleted by someone else')

    q = GLSOPT.query
    q = q.filter_by(GLOPCONO = cono)
    obj = q.first()

    if obj:
      mvcsession.entryDataset.CopyFromORM(
          'GLOPCONO;GLOPCLCD;GLOPPVST;GLOPPRST;GLOPFSTP;GLOPFSNM;GLOPFSYR;GLOPACSC;GLOPACSG;GLOPACDL;GLOPBCNO',
          'GLOPCONO;GLOPCLCD;GLOPPVST;GLOPPRST;GLOPFSTP;GLOPFSNM;GLOPFSYR;GLOPACSC;GLOPACSG;GLOPACDL;GLOPBCNO',
          obj
        )
      closingacct = glsobj.getAcct(cono, obj.GLOPCLCD)
      ficaltype = fscobj.getFiscalType(cono, obj.GLOPFSTP)
      acctstruct = glsobj.getAcctStructure(obj.GLOPACSC)
      acctcluster= glsobj.getAcctCluster(obj.GLOPACSG)
      mvcsession.entryDataset.Edit()
      mvcsession.entryDataset.SetFieldValue('GLOPCLNM', '')
      mvcsession.entryDataset.SetFieldValue('GLOPCLNM', closingacct['GLACACNM'])
      mvcsession.entryDataset.SetFieldValue('GLOPFSNM', ficaltype[2])
      mvcsession.entryDataset.SetFieldValue('GLOPSCNM', acctstruct['ACASACNM'])
      mvcsession.entryDataset.SetFieldValue('GLOPSGNM', acctcluster['CSCPCSNM'])
      mvcsession.entryDataset.Post()
    else:
      mvcsession.entryDataset.Append()
      mvcsession.entryDataset.SetFieldValue('GLOPCONO', cono)
      mvcsession.entryDataset.SetFieldValue('GLOPACDL', '-')
      mvcsession.entryDataset.SetFieldValue('GLOPPVST', 1)
      mvcsession.entryDataset.SetFieldValue('GLOPPRST', 1)
      mvcsession.entryDataset.SetFieldValue('GLOPFSTP', None)
      mvcsession.entryDataset.Post()

    mvcsession.fieldDefs.GLOPCONO.enabled = False

    return mvcsession

  def postData(self, mvcsession):
    fields = mvcsession.entryDataset.FieldsAsDict()
    q = GLSOPT.query
    q = q.filter_by(GLOPCONO = fields['GLOPCONO'])
    obj = q.first()

    td = dt.datetime.now()
    if not obj:
      if fields['GLOPCONO'] in ('', None):
        raise Exception('User account has not been setup properly')
      dobj = MSTCMP.query.filter_by(CMCPCONO = fields['GLOPCONO']).first()
      if not dobj:
        raise Exception('Default company does not exist')

      rec = GLSOPT(
              GLOPCONO  = fields['GLOPCONO'],
              GLOPCLCD  = fields['GLOPCLCD'],
              GLOPPVST  = fields['GLOPPVST'],
              GLOPPRST  = fields['GLOPPRST'],
              GLOPFSTP  = fields['GLOPFSTP'],
              GLOPFSYR  = fields['GLOPFSYR'],
              GLOPACSC  = fields['GLOPACSC'],
              GLOPACSG  = fields['GLOPACSG'],
              GLOPACDL  = fields['GLOPACDL'],
              GLOPBCNO  = fields['GLOPBCNO'],
              GLOPAUDT  = td.date().tointeger(),
              GLOPAUTM  = td.time().tointeger(),
              GLOPAUUS  = mvcsession.cookies['user_name'].encode('utf8')
            )
      if not session.transaction_started():
        session.begin()
      try:
        session.save(rec)
        session.commit()
      except:
        session.rollback()
        session.expunge(rec)
        raise
    else:
      obj.GLOPCLCD  = fields['GLOPCLCD']
      obj.GLOPPVST  = fields['GLOPPVST']
      obj.GLOPPRST  = fields['GLOPPRST']
      obj.GLOPFSTP  = fields['GLOPFSTP']
      obj.GLOPFSYR  = fields['GLOPFSYR']
      obj.GLOPACSC  = fields['GLOPACSC']
      obj.GLOPACSG  = fields['GLOPACSG']
      obj.GLOPACDL  = fields['GLOPACDL']
      obj.GLOPBCNO  = fields['GLOPBCNO']
      obj.GLOPAUDT  = td.date().tointeger()
      obj.GLOPAUTM  = td.time().tointeger()
      obj.GLOPAUUS  = mvcsession.cookies['user_name'].encode('utf8')

      if not session.transaction_started():
        session.begin()
      try:
        session.update(obj)
        session.commit()
      except:
        session.expunge(obj)
        session.rollback()
        raise

    return mvcsession

