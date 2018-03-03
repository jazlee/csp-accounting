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
__copyright__ = 'Copyright (c) 2009 Cipta Solusi Pratama'

from procsvc import *
from elixir import *
from jitutil import *
from validators import *
import datetime as dt
import sqlalchemy as sa
import ecfpool
from tbl import EFUAOB, EFUAFN, EFUSRS, EFUMOB, EFUGRP
from sqlalchemy.orm.attributes import InstrumentedAttribute

@nativeclass
class USROBJ(BusinessObject):
  """
  User Collection Object
  """

  def setUserValues(self, obj, usr_pool):
    for key in EFUSRS.__dict__.iterkeys():
      if isinstance(EFUSRS.__dict__[key], InstrumentedAttribute):
        usr_pool[key] = getattr(obj, key, None)

  def updateUserCache(self, obj):
    pool = ecfpool.getCachePool()
    usr_pool = {}
    self.setUserValues(obj,  usr_pool)
    pool.setUserDict(obj.EFUSUSID, usr_pool)
    return usr_pool

  def removeUserCache(self, obj):
    pool = ecfpool.getCachePool()
    pool.delUserDict(obj.EFUSUSID)

  def getUserInfo(self, usrname):
    pool = ecfpool.getCachePool()
    if usrname != None:
      usr_pool = pool.getUserDict(usrname)
      if usr_pool is None:
        obj = EFUSRS.get(usrname)
        if obj is not None:
          self.updateUserCache(obj, usr_pool)
    usr_pool = pool.getUserDict(usrname)
    if usr_pool:
      return (usr_pool['EFUSFSNM'], usr_pool['EFUSLSNM'],
              usr_pool['EFUSCONO'], usrname,
              usr_pool['EFUSDVNO'])
    return (None, None, None, None, None, None)

  def getUserInfoEx(self, user_name):
    ret = self.getUserInfo(user_name)
    if (ret[2] in (None, '')):
      raise Exception('Default company for user % is not assigned' % user_name)
    return ret

  def retrieveUserInfo(self, mvcsession):
    pool = ecfpool.getCachePool()
    usr_name = mvcsession.cookies['user_name'].encode('utf8')
    if usr_name != None:
      usr_pool = pool.getUserDict(usr_name)
      if usr_pool is None:
        obj = EFUSRS.query.filter_by(EFUSUSID = usr_name) \
          .first()
        if obj is not None:
          usr_pool =  self.updateUserCache(obj)
    else:
      usr_pool = pool.getUserDict(usr_name)
    if usr_pool:
      return (usr_pool['EFUSFSNM'], usr_pool['EFUSLSNM'], usr_pool['EFUSCONO'])
    else:
      return (None, None, None)

  def retrieveUserInfoEx(cls, mvcsession):
    ret = self.retrieveUserInfo(mvcsession)
    if (ret[2] in (None, '')):
      raise Exception('Default company for user % is not assigned' %
        mvcsession.cookies['user_name'].encode('utf8'))
    return ret

  def retrieveUserInfoDict(self, mvcsession):
    pool = ecfpool.getCachePool()
    usrname = mvcsession.cookies['user_name'].encode('utf8')
    usr_pool = pool.getUserDict(usrname)
    if usr_pool is None:
      obj = EFUSRS.query.filter_by(EFUSUSID = usrname) \
          .first()
      if obj is not None:
        usr_pool = self.updateUserCache(obj)
    ret_dict = {
        'USRNAME' : mvcsession.cookies['user_name'].encode('utf8'),
        'USRFNAME': None,
        'USRLNAME': None,
        'USRCONO' : None,
        'USRDVNO' : None
      }
    if usr_pool:
      ret_dict['USRFNAME']  = usr_pool['EFUSFSNM']
      ret_dict['USRLNAME']  = usr_pool['EFUSLSNM']
      ret_dict['USRCONO']   = usr_pool['EFUSCONO']
      ret_dict['USRDVNO']   = usr_pool['EFUSDVNO']
    return ret_dict

  def validateGroup(self, grpname):
    obj = EFUSRS.get(grpname)
    if (obj is not None) and (obj.EFUSUSTP == 'GRP'):
      return obj
    return None

  def retrieveUserInfoEx(self, mvcsession):
    return EFUSRS.retrieveUserInfoEx(mvcsession)

  def getUserGroups(self, usrnm):
    objs = EFUGRP.query.filter_by(EFUGUSID = usrnm).all()
    if objs:
      return [ob.EFUGGRID for ob in objs]
    return None

  def checkMVCAuth(self, usrnm, objnm, acctp):
    res = True
    ob = EFUMOB.query.filter_by(UMOUSRNM='*', UMOOBJNM='*').first()
    if not ob:
      ob = EFUMOB.query.filter_by(UMOUSRNM=usrnm, UMOOBJNM='*').first()
      if not ob:
        ob = EFUMOB.query.filter_by(UMOUSRNM='*', UMOOBJNM=objnm).first()
        if not ob:
          ob = EFUMOB.query.filter_by(UMOUSRNM=usrnm, UMOOBJNM=objnm).first()
          if not ob:
            res = False

    if res:
      chkaccess = {
          'S': ob.UMOOBJSL,
          'I': ob.UMOOBJIN,
          'U': ob.UMOOBJUP,
          'D': ob.UMOOBJDL,
          'X': ob.UMOOBJEX,
        }
      for fnctp in chkaccess.keys():
        if fnctp == acctp:
          res = chkaccess[fnctp] == 1

    return res

  def checkAPIObj(self, usrnm, objnm):
    res = True
    ob = EFUAOB.query.filter_by(UAOUSRNM='*', UAOOBJNM='*').first()
    if not ob:
      ob = EFUAOB.query.filter_by(UAOUSRNM=usrnm, UAOOBJNM='*').first()
      if not ob:
        ob = EFUAOB.query.filter_by(UAOUSRNM='*', UAOOBJNM=objnm).first()
        if not ob:
          ob = EFUAOB.query.filter_by(UAOUSRNM=usrnm, UAOOBJNM=objnm).first()
          if not ob:
            res = False
    return res

  def checkAPIFnc(self, usrnm, objnm, fncnm, acctp):
    res = True
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
    return res

  def checkAPIAuth(self, usrnm, objnm, fncnm, acctp):
    res = self.checkAPIObj(usrnm, objnm)
    if res:
      res = self.checkAPIFnc(usrnm, objnm, fncnm, acctp)
    return res

  def initDefUser(self):
    cnt = EFUSRS.query.filter(None).count()
    if cnt == 0:
      if not session.transaction_started():
        session.begin()

      usnm = EFUSRS(EFUSUSID='ADMIN', EFUSPSWD='AB4154A7C451F56E9B7FF1537758DDD0C619F8BE', \
        EFUSFSNM='SYSTEM', EFUSLSNM='ADMINISTRATOR', EFUSEMAD='admin@ciptasolusi.com', EFUSSTAT=1, \
        EFUSDESC='SYSTEM ADMINISTRATOR', EFUSUSTP='USR')
      grnm = EFUSRS(EFUSUSID='ADMINISTRATOR', EFUSUSTP='GRP', EFUSDESC='ADMINISTRATOR GROUP', EFUSSTAT=1)
      usob = EFUAOB(UAOUSRNM='ADMINISTRATOR', UAOOBJNM='*')
      usfn = EFUAFN(UAFUSRNM='ADMINISTRATOR', UAFOBJNM='*', UAFFNCNM='*', UAFFNCSL=True, UAFFNCIN=True, UAFFNCUP=True, UAFFNCDL=True, UAFFNCEX=True)
      fumb = EFUMOB(UMOUSRNM='ADMINISTRATOR', UMOOBJNM='*', UMOOBJSL=1, UMOOBJIN=1, UMOOBJUP=1, UMOOBJDL=1, UMOOBJEX=1)
      usgp = EFUGRP(EFUGGRID='ADMINISTRATOR', EFUGUSID = 'ADMIN', EFUGFSNM = 'SYSTEM', EFUGLSNM='ADMINISTRATOR')

      self.setAuditFields(usnm, 'ADMIN')
      self.setAuditFields(grnm, 'ADMIN')
      self.setAuditFields(usob, 'ADMIN')
      self.setAuditFields(usfn, 'ADMIN')
      self.setAuditFields(fumb, 'ADMIN')
      self.setAuditFields(usgp, 'ADMIN')

      session.add(usnm)
      session.add(grnm)
      session.add(usob)
      session.add(usfn)
      session.add(fumb)
      session.add(usgp)

      session.commit()
      session.close()

  def initDatabase(self):
    self.initDefUser()
