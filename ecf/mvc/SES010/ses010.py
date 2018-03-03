#
# Copyright (c) 2009 Cipta Solusi Pratama. All rights reserved.
#
# This product and it's source code is protected by patents, copyright laws and
# international copyright treaties, as well as other intellectual property
# laws and treaties. The product is licensed, not sold.
#
# The source code and sample programs in this package or parts hereof
# as well as the documentation shall not be copied, modified or redistributed
# without permission, explicit or implied, of the author.
#


__author__    = 'Jaimy Azle'
__version__   = '1.0'
__copyright__ = 'Copyright (c) 2008 Jaimy Azle'

from mvcsvc import *
import datetime as dt
import sqlalchemy as sa
from elixir import *
from validators import *
import _ecfpyutils
from tbl import EFUSRS, MSTCMP

class SES010(MVCController):
  """
  User Management
  """
  _description = 'User Management'
  _active = True
  _supported_functions = (MVCFuncNew, MVCFuncOpen, MVCFuncShow, MVCFuncCopy, MVCFuncDelete)
  _model_binder = MVCModelBinder(EFUSRS)

  EFUSUSID    = MVCField(MVCTypeField + MVCTypeList, String(24), label = 'User Name', charcase=ecUpperCase)
  EFUSPSWD    = MVCField(MVCTypeField, String(64), label = 'Password')
  EFUSFSNM    = MVCField(MVCTypeField + MVCTypeList, String(24), label = 'First Name')
  EFUSLSNM    = MVCField(MVCTypeField + MVCTypeList, String(24), label = 'Last Name')
  EFUSEMAD    = MVCField(MVCTypeField, String(48), label = 'E-Mail')
  EFUSUSTP    = MVCField(MVCTypeField + MVCTypeList+MVCTypeParam, String(3), label = 'User type',
                  choices={
                      'User': 'USR',
                      'Group': 'GRP'
                  }, synchronized=True)
  EFUSDESC    = MVCField(MVCTypeField + MVCTypeList, String(64), label = 'Description')
  EFUSCONO    = MVCField(MVCTypeField, String(3), label = 'Def. Company', charcase=ecUpperCase, browseable=True, synchronized=True)
  EFUSCONM    = MVCField(MVCTypeField, String(24), label = 'Def. Company Name', enabled=False)
  EFUSDVNO    = MVCField(MVCTypeField, String(3), label = 'Def. Division', charcase=ecUpperCase, browseable=True, synchronized=True)
  EFUSDVNM    = MVCField(MVCTypeField, String(24), label = 'Def. Division', enabled=False)
  EFUSSTAT    = MVCField(MVCTypeField + MVCTypeParam, Integer(), label = 'Status', choices = {'Active':'1', 'Inactive': '0'})

  def initView(self, mvcsession):
    '''Initialize the program'''
    mvcsession.extFunctions = ( MVCExtFunction('User group', 'SES011', params = {'EFUGGRID':'%f:EFUSUSID'}), )
    return mvcsession

  def lookupView(self, session, fieldName):
    '''Define lookup metadata for specified field'''
    ret = MVCLookupDef('','')
    if fieldName == 'EFUSCONO':
      ret.svcname = 'CMN100'
      ret.retfield = 'CMCPCONO'
    if fieldName == 'EFUSDVNO':
      ret.svcname = 'CMN110'
      ret.retfield = 'CMDVDVNO'
      ret.params = {'CMDVCONO':'%f:EFUSCONO'}
    return ret

  def synchronizeData(self, mvcsession, fieldName, fieldType):
    '''Synchronize data retrieved from user input'''
    fields = mvcsession.entryDataset.FieldsAsDict()
    proxy = self.getBusinessObjectProxy()
    cmpobj = proxy.getObject('CMPOBJ')
    if (fieldName == 'EFUSCONO'):
      lst = cmpobj.getCompany(fields['EFUSCONO'])
      mvcsession.entryDataset.Edit()
      mvcsession.entryDataset.SetFieldValue('EFUSCONO', lst[0])
      mvcsession.entryDataset.SetFieldValue('EFUSCONM', lst[1])
      mvcsession.entryDataset.Post()
      self.synchronizeData(mvcsession, 'EFUSDVNO', fieldType)
    if (fieldName == 'EFUSDVNO'):
      division = cmpobj.getDivision(fields['EFUSCONO'], fields['EFUSDVNO'])
      mvcsession.entryDataset.Edit()
      mvcsession.entryDataset.SetFieldValue('EFUSDVNO', division[2])
      mvcsession.entryDataset.SetFieldValue('EFUSDVNM', division[3])
      mvcsession.entryDataset.Post()
    if (fieldName == 'EFUSUSTP'):
      enable = fields['EFUSUSTP'] == 'USR'
      mvcsession.fieldDefs.EFUSFSNM.enabled = enable
      mvcsession.fieldDefs.EFUSLSNM.enabled = enable
      mvcsession.fieldDefs.EFUSCONO.enabled = enable
      mvcsession.fieldDefs.EFUSDVNO.enabled = enable
      mvcsession.fieldDefs.EFUSEMAD.enabled = enable
      mvcsession.fieldDefs.EFUSPSWD.enabled = enable
    return mvcsession

  def initializeParam(self, mvcsession, query):
    '''Initialize parameters'''
    if mvcsession.paramDataset.RecordCount == 0:
      mvcsession.paramDataset.Append()
      mvcsession.paramDataset.SetFieldValue('EFUSSTAT', 1)
      mvcsession.paramDataset.Post()
    fields = mvcsession.paramDataset.FieldsAsDict()
    if (fields['EFUSSTAT'] != None):
      query = query.filter_by(EFUSSTAT = fields['EFUSSTAT'])
    if (fields['EFUSUSTP'] not in (None, '')):
      query = query.filter_by(EFUSUSTP = fields['EFUSUSTP'])
    return query

  def initializeData(self, mvcsession):
    '''Initializing data'''
    # Setup default value
    mvcsession.entryDataset.Append()
    mvcsession.entryDataset.SetFieldValue('EFUSSTAT', 1)
    mvcsession.entryDataset.SetFieldValue('EFUSUSTP', 'USR')
    mvcsession.entryDataset.Post()
    return mvcsession

  def afterRetrieveData(self, mvcsession, obj):
    '''Event triggered after retrieving data'''
    if mvcsession.execType == MVCExecEdit:
      fields = mvcsession.entryDataset.FieldsAsDict()
      enable = fields['EFUSUSTP'] == 'USR'
      mvcsession.fieldDefs.EFUSUSID.enabled = False
      mvcsession.fieldDefs.EFUSUSTP.enabled = False
      mvcsession.fieldDefs.EFUSFSNM.enabled = enable
      mvcsession.fieldDefs.EFUSLSNM.enabled = enable
      mvcsession.fieldDefs.EFUSCONO.enabled = enable
      mvcsession.fieldDefs.EFUSDVNO.enabled = enable
      mvcsession.fieldDefs.EFUSEMAD.enabled = enable
      mvcsession.fieldDefs.EFUSPSWD.enabled = enable
    return (mvcsession, obj)

  def postData(self, mvcsession):
    '''Post data into persistent storage'''
    fields = mvcsession.entryDataset.FieldsAsDict()
    now = dt.datetime.now()
    proxy = self.getBusinessObjectProxy()
    usrobj = proxy.getObject('USROBJ')
    if mvcsession.execType in (MVCExecAppend, MVCExecCopy):
      q = EFUSRS.query
      q = q.filter_by(EFUSUSID = fields['EFUSUSID'])
      obj = q.first()
      if obj:
        raise Exception('existing record is found in the database')

      passwd = fields['EFUSPSWD']
      if passwd:
        password = _ecfpyutils.getHashKey(passwd)
      else:
        password = ''
      obj = EFUSRS(
        EFUSUSID = fields['EFUSUSID'],
        EFUSPSWD = password,
        EFUSFSNM = fields['EFUSFSNM'],
        EFUSLSNM = fields['EFUSLSNM'],
        EFUSEMAD = fields['EFUSEMAD'],
        EFUSDESC = fields['EFUSDESC'],
        EFUSCONO = fields['EFUSCONO'],
        EFUSCONM = fields['EFUSCONM'],
        EFUSDVNO = fields['EFUSDVNO'],
        EFUSDVNM = fields['EFUSDVNM'],
        EFUSSTAT = fields['EFUSSTAT'],
        EFUSUSTP = fields['EFUSUSTP'],
        EFUSAUDT = now.date().tointeger(),
        EFUSAUTM = now.time().tointeger(),
        EFUSAUUS = mvcsession.cookies['user_name'].encode('utf8')
      )
      if not session.transaction_started():
        session.begin()
      try:
        session.save(obj)
        session.commit()
      except:
        session.rollback()
        raise
    if mvcsession.execType == MVCExecEdit:
      q = EFUSRS.query
      q = q.filter_by(EFUSUSID = fields['EFUSUSID'])
      obj = q.first()
      if not obj:
        raise Exception('The record could not be found in the database')
      oldpwd = obj.EFUSPSWD
      mvcsession.entryDataset.CopyIntoORM(
        'EFUSUSID;EFUSPSWD;EFUSFSNM;EFUSLSNM;EFUSEMAD;EFUSDESC;EFUSCONO;EFUSCONM;EFUSSTAT;EFUSDVNO;EFUSDVNM;EFUSUSTP',
        'EFUSUSID;EFUSPSWD;EFUSFSNM;EFUSLSNM;EFUSEMAD;EFUSDESC;EFUSCONO;EFUSCONM;EFUSSTAT;EFUSDVNO;EFUSDVNM;EFUSUSTP',
        obj)
      if oldpwd != obj.EFUSPSWD:
        obj.EFUSPSWD = _ecfpyutils.getHashKey(obj.EFUSPSWD)
      obj.EFUSAUDT = now.date().tointeger()
      obj.EFUSAUTM = now.time().tointeger()
      obj.EFUSAUUS = mvcsession.cookies['user_name'].encode('utf8')
      if not session.transaction_started():
        session.begin()
      try:
        session.update(obj)
        usrobj.updateUserCache(obj)
        session.commit()
      except:
        session.rollback()
        session.expunge(obj)
        raise

    if mvcsession.execType == MVCExecDelete:
      q = EFUSRS.query
      q = q.filter_by(EFUSUSID = fields['EFUSUSID'])
      obj = q.first()
      if not obj:
        raise Exception('record could not be found in the database')
      if not session.transaction_started():
        session.begin()
      try:
        usrobj.removeUserCache(obj)
        session.delete(obj)
        session.commit()
      except:
        session.rollback()
    return mvcsession

  def finalizeView(self, mvcsession):
    return mvcsession