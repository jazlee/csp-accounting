from intsvc import INTService, INTLocalService
from tbl import EFUAOB, EFUAFN, EFUSRS, EFUMOB
from tbl import EFJBLS, MSTCMP, CMPDIV
import _ecfpyutils
import datetime as dt
import elixir as el
from sqlalchemy.orm.attributes import InstrumentedAttribute
from jitutil import *

@nativeclass
class INTAuthService(INTService):
  def __init__(self, name='__INTAUTHSVC__'):
    super(INTAuthService, self).__init__(name)
    self.joinGroup('__INTSVC__')
    self.exportMethod(self.checkAPIAuth)
    self.exportMethod(self.checkUSRAuth)
    self.exportMethod(self.changeUSRPasswd)
    self.exportMethod(self.verifyAPIAccess)
    self.exportMethod(self.checkMVCAuth)
    self.exportMethod(self.verifyMVCAccess)

  def checkUSRAuth(self, usrnm, passwd):
    res = True
    password = _ecfpyutils.getHashKey(passwd)
    try:
      ob = EFUSRS.query.filter_by(EFUSUSID=usrnm, EFUSPSWD=password, EFUSSTAT=1, EFUSUSTP = 'USR').first()
      if (not ob):
        # print 'Username "%s" could not be found or password "%s" does not match' % (usrnm, passwd)
        res = False
    finally:
      el.session.close()
    return res

  def changeUSRPasswd(self, usrnm, oldpasswd, newpasswd):
    try:
      password = _ecfpyutils.getHashKey(oldpasswd)
      ob = EFUSRS.query.filter_by(EFUSUSID=usrnm, EFUSPSWD=password).first()
      if ob:
        password = _ecfpyutils.getHashKey(newpasswd)
        ob.EFUSPSWD = password
        if not el.session.transaction_started():
          el.session.begin()
        try:
          el.session.update(obj)
        except:
          el.session.rollback()
          raise
      else:
        raise Exception('Username could not be found or password does not match')
    finally:
      session.close()

  def checkAPIObj(self, usrnm, objnm):
    res = True
    try:
      ob = EFUAOB.query.filter_by(UAOUSRNM='*', UAOOBJNM='*').first()
      if not ob:
        ob = EFUAOB.query.filter_by(UAOUSRNM=usrnm, UAOOBJNM='*').first()
        if not ob:
          ob = EFUAOB.query.filter_by(UAOUSRNM='*', UAOOBJNM=objnm).first()
          if not ob:
            ob = EFUAOB.query.filter_by(UAOUSRNM=usrnm, UAOOBJNM=objnm).first()
            if not ob:
              res = False
    finally:
      el.session.close()
    return res

  def verifyAPIAccess(self, usrnm, objnm):
    return self.checkAPIObj(usrnm, objnm)

  def checkAPIFnc(self, usrnm, objnm, fncnm, acctp):
    res = True
    try:
      ob = EFUAFN.query.filter_by(UAFUSRNM='*', UAFOBJNM='*', UAFFNCNM='*').first()
      if not ob:
        ob = EFUAFN.query.filter_by(UAFUSRNM=usrnm, UAFOBJNM='*', UAFFNCNM='*').first()
        if not ob:
          ob = EFUAFN.query.filter_by(UAFUSRNM=usrnm, UAFOBJNM=objnm, UAFFNCNM='*').first()
          if not ob:
            ob = EFUAFN.query.filter_by(UAFUSRNM=usrnm, UAFOBJNM=objnm, UAFFNCNM=fncnm).first()
            if not ob:
              res = False
      if res:
        chkaccess = {
            'S': ob.UAFFNCSL,
            'I': ob.UAFFNCIN,
            'U': ob.UAFFNCUP,
            'D': ob.UAFFNCDL,
            'X': ob.UAFFNCEX,
          }
        for fnctp in chkaccess.keys():
          if fnctp == acctp:
            res = chkaccess[fnctp] == 1
    finally:
      el.session.close()
    return res

  def checkAPIAuth(self, usrnm, objnm, fncnm, acctp):
    res = False
    try:
      proxy = self.getBusinessObjectProxy()
      usrobj = proxy.getObject('USROBJ')
      res = usrobj.checkAPIAuth(usrnm, objnm, fncnm, acctp)
      if not res:
        grps = usrobj.getUserGroups(usrnm)
        if grps:
          for grp in grps:
            res = usrobj.checkAPIAuth(grp, objnm, fncnm, acctp)
            if res:
              break
    finally:
      el.session.close()
    return res

  def verifyMVCAccess(self, usrnm, objnm, acctp):
    res = True
    try:
      ob = EFUMOB.query.filter_by(UMOUSRNM='*', UMOOBJNM='*').first()
      if not ob:
        ob = EFUMOB.query.filter_by(UMOUSRNM=usrnm, UMOOBJNM='*').first()
        if not ob:
          ob = EFUMOB.query.filter_by(UMOUSRNM='*', UMOOBJNM=objnm).first()
          if not ob:
            ob = EFUMOB.query.filter_by(UMOUSRNM=usrnm, UMOOBJNM=objnm).first()
            if not ob:
              res = False
    finally:
      el.session.close()
    return res

  def checkMVCAuth(self, usrnm, objnm, acctp):
    res = False
    try:
      proxy = self.getBusinessObjectProxy()
      usrobj = proxy.getObject('USROBJ')
      res = usrobj.checkMVCAuth(usrnm, objnm, acctp)
      if not res:
        grps = usrobj.getUserGroups(usrnm)
        if grps:
          for grp in grps:
            res = usrobj.checkMVCAuth(grp, objnm, acctp)
            if res:
              break
    finally:
      el.session.close()
    return res

INTAuthService()

@nativeclass
class INTJobService(INTService):
  def __init__(self, name='__INTJOBSVC__'):
    super(INTJobService, self).__init__(name)
    self.joinGroup('__INTSVC__')
    self.exportMethod(self.checkJob)

  def checkUnprocessedJob(self):
    q = EFJBLS.query
    q = q.filter_by(JBLSPRST = 0)
    objs = q.all()
    date_now = dt.datetime.now()
    for obj in objs:
      if (obj.JBLSRPDT != None) and (obj.JBLSRPDT != 0):
        date_request = dt.date.frominteger(obj.JBLSRPDT)
        date_span = date_now.date() - date_request
        if date_span >= dt.timedelta(0):
          if (obj.JBLSRPTM != None) and (obj.JBLSRPTM != 0):
            time_request = dt.time.frominteger(obj.JBLSRPTM)
            date_span = date_now.time() - time_request
            if date_span >= dt.timedelta(0):
              jbrun = _ecfpyutils.runJobID(obj.JBLSIDNM)
          else:
            jbrun = _ecfpyutils.runJobID(obj.JBLSIDNM)
      else:
        jbrun = _ecfpyutils.runJobID(obj.JBLSIDNM)

  def checkProcessedJob(self):
    q = EFJBLS.query
    q = q.filter_by(JBLSPRST = 10)
    objs = q.all()
    for obj in objs:
      process_exist = _ecfpyutils.checkJobID(obj.JBLSIDNM)
      if not process_exist:
        # mark as failed
        obj.JBLSPRST = 99
        if not el.session.transaction_started():
          el.session.begin()
        try:
          el.session.update(obj)
        except:
          el.session.rollback()
          raise

  def checkJob(self):
    try:
      self.checkUnprocessedJob()
      self.checkProcessedJob()
    finally:
      el.session.close()

INTJobService()

class INTSysService(INTService):
  def __init__(self, name='__INTSYSSVC__'):
    super(INTSysService, self).__init__(name)
    self.joinGroup('__INTSVC__')
    self.exportMethod(self.getSystemInfo)

  def getSystemInfo(self, usr_name):
    retdict = {}
    usr = EFUSRS.get(usr_name)
    if usr:
      retdict['user_name'] = usr.EFUSUSID
      retdict['first_name'] = usr.EFUSFSNM
      retdict['last_name'] = usr.EFUSLSNM

      auditfields = ('AUDT', 'AUTM', 'AUUS')

      if usr.EFUSCONO:
        mstcmp = MSTCMP.get(usr.EFUSCONO)
        if mstcmp:
          for key in MSTCMP.__dict__.iterkeys():
            if isinstance(MSTCMP.__dict__[key], InstrumentedAttribute) and \
              (key[4:] not in auditfields):
                val = getattr(mstcmp, key, None)
                retdict[key] = val
        mstdiv = CMPDIV.get((usr.EFUSCONO, usr.EFUSDVNO))
        if mstdiv:
          for key in CMPDIV.__dict__.iterkeys():
            if isinstance(CMPDIV.__dict__[key], InstrumentedAttribute) and \
              (key[4:] not in auditfields):
                val = getattr(mstdiv, key, None)
                retdict[key] = val
    values = [(key, value) for key, value in retdict.iteritems()]
    return tuple(values)

INTSysService()