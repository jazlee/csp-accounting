from apisvc import *
from intsvc import INTLocalService
from sqlalchemy import *
from elixir import *
from tbl import EFUSRS, EFUAOB, EFUAFN
import _ecfpyutils

boolintvalue = {
  True: 1,
  False: 0
}

intboolvalue = {
  1:True,
  0:False
}

class ECFSYSAPI(RPCService):
  _description = 'Internal server services'
  _active = True
  _version='1.0'

  manageuser = RPCDatasetMethod(
                  'Method for managing user',
                  RPCField('EFUSUSID', RPCTypeInputOutput, String(24), 'User ID'),
                  RPCField('EFUSPSWD', RPCTypeInputOutput, String(64), 'Password'),
                  RPCField('EFUSFSNM', RPCTypeInputOutput, String(24), 'First Name'),
                  RPCField('EFUSLSNM', RPCTypeInputOutput, String(24), 'Last Name'),
                  RPCField('EFUSEMAD', RPCTypeInputOutput, String(48), 'Email Address'),
                  RPCField('EFUSDESC', RPCTypeInputOutput, String(64), 'Description'),
                  RPCField('EFUSSTAT', RPCTypeInputOutput, Integer(), 'Status'),
                  methodname='MANAGEUSER',
                  active=True)

  usrchgpasswd = RPCMethod(
                  'Method for changing user password',
                  RPCParam('username', 'User Name'),
                  RPCParam('oldpasswd', 'Old Password'),
                  RPCParam('newpasswd', 'New Password'),
                  methodname='USRCHGPASSWD',
                  active=True)


  usrobjectlist = RPCDatasetMethod(
                  'List of user access for API object',
                  RPCField('UAOUSRNM', RPCTypeInputOutput, String(24), 'User Name'),
                  RPCField('UAOOBJNM', RPCTypeInputOutput, String(32), 'API Object Name'),
                  methodname='USROBJECTLIST',
                  active=True)

  usrmethodlist = RPCDatasetMethod(
                  'List of user access for object methods',
                  RPCField('UAFUSRNM', RPCTypeInputOutput, String(24), 'User Name'),
                  RPCField('UAFOBJNM', RPCTypeInputOutput, String(32), 'API Object Name'),
                  RPCField('UAFFNCNM', RPCTypeInputOutput, String(32), 'API Method Name'),
                  RPCField('UAFFNCSL', RPCTypeInputOutput, Integer(), 'Access to select method'),
                  RPCField('UAFFNCIN', RPCTypeInputOutput, Integer(), 'Access to insert method'),
                  RPCField('UAFFNCUP', RPCTypeInputOutput, Integer(), 'Access to update method'),
                  RPCField('UAFFNCDL', RPCTypeInputOutput, Integer(), 'Access to delete method'),
                  RPCField('UAFFNCEX', RPCTypeInputOutput, Integer(), 'Access to execute method'),
                  methodname='USRMETHODLIST',
                  active=True)

  apiobjectlist = RPCDatasetMethod(
                  'Method for getting API Object list',
                  RPCField('EFAPOBID', RPCTypeOutput, String(24), 'Object Name'),
                  RPCField('EFAPOBDS', RPCTypeOutput, String(64), 'Description'),
                  RPCField('EFAPOBST', RPCTypeOutput, Integer(), 'Status'),
                  methodname='APIOBJECTLIST',
                  active=True
                  )

  apimethodlist = RPCDatasetMethod(
                  'Method for getting API Object list',
                  RPCField('EFAPOBID', RPCTypeInputOutput, String(24), 'Object Name'),
                  RPCField('EFAPFNNM', RPCTypeOutput, String(48), 'Method Name'),
                  RPCField('EFAPFNDS', RPCTypeOutput, String(64), 'Description'),
                  RPCField('EFAPFNPD', RPCTypeOutput, String(8), 'Plain/Dataset Method'),
                  RPCField('EFAPFNST', RPCTypeOutput, Integer(), 'Status'),
                  RPCField('EFAPFNTP', RPCTypeOutput, String(8), 'Execution Support Types'),
                  methodname='APIMETHODLIST',
                  active=True
                  )

  def manageuser_select(self, rpcsession):
    fields = rpcsession.inputDataset.FieldsAsDict()
    q = EFUSRS.query
    if fields['EFUSUSID'] != None:
      q = q.filter_by(EFUSUSID = fields['EFUSUSID'])
    if fields['EFUSSTAT'] != None:
      q = q.filter_by(EFUSSTAT = fields['EFUSSTAT'])
    objs = q.order_by(asc(EFUSRS.EFUSUSID)).all()
    for obj in objs:
      rpcsession.outputDataset.Append()
      rpcsession.outputDataset.SetFieldValue('EFUSUSID', obj.EFUSUSID)
      rpcsession.outputDataset.SetFieldValue('EFUSPSWD', obj.EFUSPSWD)
      rpcsession.outputDataset.SetFieldValue('EFUSFSNM', obj.EFUSFSNM)
      rpcsession.outputDataset.SetFieldValue('EFUSLSNM', obj.EFUSLSNM)
      rpcsession.outputDataset.SetFieldValue('EFUSEMAD', obj.EFUSEMAD)
      rpcsession.outputDataset.SetFieldValue('EFUSDESC', obj.EFUSDESC)
      rpcsession.outputDataset.SetFieldValue('EFUSSTAT', obj.EFUSSTAT)
      rpcsession.outputDataset.Post()

  def manageuser_insert(self, rpcsession):
    fields = rpcsession.inputDataset.FieldsAsDict()
    obj = EFUSRS.query.filter_by(EFUSUSID = fields['EFUSUSID']).first()
    if obj:
      raise Exception('existing user id found in the database')

    passwd = fields['EFUSPSWD']
    if passwd:
      password = _ecfpyutils.getHashKey(passwd)
    else:
      password = ''

    rec = EFUSRS(
      EFUSUSID = fields['EFUSUSID'],
      EFUSPSWD = password,
      EFUSFSNM = fields['EFUSFSNM'],
      EFUSLSNM = fields['EFUSLSNM'],
      EFUSEMAD = fields['EFUSEMAD'],
      EFUSDESC = fields['EFUSDESC'],
      EFUSSTAT = fields['EFUSSTAT'])
    if not session.transaction_started():
      session.begin()
    try:
      session.save(rec)
      session.commit()
    except:
      session.rollback()
      session.clear()
      raise

  def manageuser_update(self, rpcsession):
    fields = rpcsession.inputDataset.FieldsAsDict()
    obj = EFUSRS.query.filter_by(EFUSUSID = fields['EFUSUSID']).first()
    if not obj:
      raise Exception('user id could be found in the database')

    if obj.EFUSPSWD != fields['EFUSPSWD']:
      passwd = fields['EFUSPSWD']
      if passwd:
        password = _ecfpyutils.getHashKey(passwd)
      else:
        password = ''
      obj.EFUSPSWD = _ecfpyutils.getHashKey(passwd)

    obj.EFUSFSNM = fields['EFUSFSNM']
    obj.EFUSLSNM = fields['EFUSLSNM']
    obj.EFUSEMAD = fields['EFUSEMAD']
    obj.EFUSDESC = fields['EFUSDESC']
    obj.EFUSSTAT = fields['EFUSSTAT']

    if not session.transaction_started():
      session.begin()
    try:
      session.update(obj)
      session.commit()
    except:
      session.rollback()
      session.clear()
      raise

  def manageuser_delete(self, rpcsession):
    fields = rpcsession.inputDataset.FieldsAsDict()
    obj = EFUSRS.query.filter_by(EFUSUSID = fields['EFUSUSID']).first()
    if not obj:
      raise Exception('user id could be found in the database')
    if not session.transaction_started():
      session.begin()
    try:
      session.delete(obj)
      session.commit()
    except:
      session.rollback()
      session.clear()
      raise

  def usrchgpasswd_exec(self, usrname, oldpasswd, newpasswd):
    svc = INTLocalService('__INTAUTHSVC__')
    svc.changeUSRPasswd(usrname, oldpasswd, newpasswd)
    return None

  def apiobjectlist_select(self, rpcsession):
    svc = APIInvocationService()
    objlist = svc.objectList()
    for obj in objlist:
      rpcsession.outputDataset.Append()
      rpcsession.outputDataset.SetFieldValue('EFAPOBID', obj[0])
      rpcsession.outputDataset.SetFieldValue('EFAPOBDS', obj[1])
      rpcsession.outputDataset.SetFieldValue('EFAPOBST', boolintvalue[obj[2]])
      rpcsession.outputDataset.Post()

  def apimethodlist_select(self, rpcsession):
    svc = APIInvocationService()
    fields = rpcsession.inputDataset.FieldsAsDict()
    objname = fields['EFAPOBID']
    if objname:
      metlist = svc.methodList(objname)
      for obj in objlist:
        rpcsession.outputDataset.Append()
        rpcsession.outputDataset.SetFieldValue('EFAPOBID', objname)
        rpcsession.outputDataset.SetFieldValue('EFAPFNNM', obj[0])
        rpcsession.outputDataset.SetFieldValue('EFAPFNDS', obj[1])
        rpcsession.outputDataset.SetFieldValue('EFAPFNPD', obj[2])
        rpcsession.outputDataset.SetFieldValue('EFAPFNST', boolintvalue[obj[3]])
        rpcsession.outputDataset.SetFieldValue('EFAPFNTP', obj[4])
        rpcsession.outputDataset.Post()

  def usrobjectlist_select(self, rpcsession):
    fields = rpcsession.inputDataset.FieldsAsDict()
    q = EFUAOB.query
    if fields['UAOUSRNM'] != None:
      q = q.filter_by(UAOUSRNM = fields['UAOUSRNM'])
    if fields['UAOOBJNM'] != None:
      q = q.filter_by(UAOOBJNM = fields['UAOOBJNM'])
    objs = q.order_by(asc(EFUAOB.UAOUSRNM)).all()
    for obj in objs:
      rpcsession.outputDataset.Append()
      rpcsession.outputDataset.SetFieldValue('UAOUSRNM', obj.UAOUSRNM)
      rpcsession.outputDataset.SetFieldValue('UAOOBJNM', obj.UAOOBJNM)
      rpcsession.outputDataset.Post()

  def usrobjectlist_insert(self, rpcsession):
    fields = rpcsession.inputDataset.FieldsAsDict()
    q = EFUAOB.query.filter_by(UAOUSRNM = fields['UAOUSRNM'],
          UAOOBJNM = fields['UAOOBJNM'])
    obj = q.order_by(asc(EFUAOB.UAOUSRNM)).first()
    if obj:
      raise Exception('user access for specified object has already exist')

    obj = EFUAOB(
      UAOUSRNM = fields['UAOUSRNM'],
      UAOOBJNM = fields['UAOOBJNM'])
    if not session.transaction_started():
      session.begin()
    try:
      session.save(obj)
      session.commit()
    except:
      session.rollback()
      session.clear()
      raise

  def usrobjectlist_delete(self, rpcsession):
    fields = rpcsession.inputDataset.FieldsAsDict()
    q = EFUAOB.query.filter_by(UAOUSRNM = fields['UAOUSRNM'],
          UAOOBJNM = fields['UAOOBJNM'])
    obj = q.order_by(asc(EFUAOB.UAOUSRNM)).first()
    if not obj:
      raise Exception('user access for specified object does not exist')
    if not session.transaction_started():
      session.begin()
    try:
      session.delete(obj)
      session.commit()
    except:
      session.rollback()
      session.clear()
      raise

  def usrmethodlist_select(self, rpcsession):
    fields = rpcsession.inputDataset.FieldsAsDict()
    q = EFUAFN.query
    if fields['UAFUSRNM'] != None:
      q = q.filter_by(UAFUSRNM = fields['UAFUSRNM'])
    if fields['UAFOBJNM'] != None:
      q = q.filter_by(UAFOBJNM = fields['UAFOBJNM'])
    if fields['UAFFNCNM'] != None:
      q = q.filter_by(UAFFNCNM = fields['UAFFNCNM'])
    objs = q.order_by(asc(EFUAFN.UAFUSRNM)).all()
    for obj in objs:
      rpcsession.outputDataset.Append()
      rpcsession.outputDataset.SetFieldValue('UAFUSRNM', obj.UAFUSRNM)
      rpcsession.outputDataset.SetFieldValue('UAFOBJNM', obj.UAFOBJNM)
      rpcsession.outputDataset.SetFieldValue('UAFFNCNM', obj.UAFFNCNM)
      rpcsession.outputDataset.SetFieldValue('UAFFNCSL', boolintvalue[obj.UAFFNCSL])
      rpcsession.outputDataset.SetFieldValue('UAFFNCIN', boolintvalue[obj.UAFFNCIN])
      rpcsession.outputDataset.SetFieldValue('UAFFNCUP', boolintvalue[obj.UAFFNCUP])
      rpcsession.outputDataset.SetFieldValue('UAFFNCDL', boolintvalue[obj.UAFFNCDL])
      rpcsession.outputDataset.SetFieldValue('UAFFNCEX', boolintvalue[obj.UAFFNCEX])
      rpcsession.outputDataset.Post()

  def usrmethodlist_insert(self, rpcsession):
    fields = rpcsession.inputDataset.FieldsAsDict()
    q = EFUAFN.query.filter_by(
      UAFUSRNM = fields['UAFUSRNM'],
      UAFOBJNM = fields['UAFOBJNM'],
      UAFFNCNM = fields['UAFFNCNM']
      )
    obj = q.order_by(asc(EFUAFN.UAFUSRNM)).first()
    if obj:
      raise Exception('existing record has been found in the database')

    rec = EFUAFN(
      UAFUSRNM = fields['UAFUSRNM'],
      UAFOBJNM = fields['UAFOBJNM'],
      UAFFNCNM = fields['UAFFNCNM'],
      UAFFNCSL = intboolvalue[fields['UAFFNCSL']],
      UAFFNCIN = intboolvalue[fields['UAFFNCIN']],
      UAFFNCUP = intboolvalue[fields['UAFFNCUP']],
      UAFFNCDL = intboolvalue[fields['UAFFNCDL']],
      UAFFNCEX = intboolvalue[fields['UAFFNCEX']])
    if not session.transaction_started():
      session.begin()
    try:
      session.save(rec)
      session.commit()
    except:
      session.rollback()
      session.clear()
      raise

  def usrmethodlist_update(self, rpcsession):
    fields = rpcsession.inputDataset.FieldsAsDict()
    obj = EFUAFN.query.filter_by(
      UAFUSRNM = fields['UAFUSRNM'],
      UAFOBJNM = fields['UAFOBJNM'],
      UAFFNCNM = fields['UAFFNCNM']).first()
    if not obj:
      raise Exception('user id could be found in the database')

    obj.UAFFNCSL = intboolvalue[fields['UAFFNCSL']]
    obj.UAFFNCIN = intboolvalue[fields['UAFFNCIN']]
    obj.UAFFNCUP = intboolvalue[fields['UAFFNCUP']]
    obj.UAFFNCDL = intboolvalue[fields['UAFFNCDL']]
    obj.UAFFNCEX = intboolvalue[fields['UAFFNCEX']]

    if not session.transaction_started():
      session.begin()
    try:
      session.update(obj)
      session.commit()
    except:
      session.rollback()
      session.clear()
      raise

  def usrmethodlist_delete(self, rpcsession):
    fields = rpcsession.inputDataset.FieldsAsDict()
    obj = EFUAFN.query.filter_by(
      UAFUSRNM = fields['UAFUSRNM'],
      UAFOBJNM = fields['UAFOBJNM'],
      UAFFNCNM = fields['UAFFNCNM']).first()
    if not obj:
      raise Exception('user access for specified object does not exist')
    if not session.transaction_started():
      session.begin()
    try:
      session.delete(obj)
      session.commit()
    except:
      session.rollback()
      session.clear()
      raise
