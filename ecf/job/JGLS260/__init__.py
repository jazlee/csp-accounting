from elixir import *
from jobsvc import *
import datetime as dt
import ecflogger
from sqlalchemy import sql
from sqlalchemy.sql import operators
from sqlalchemy.orm.attributes import InstrumentedAttribute
import sqlalchemy as sa
import decimal as dcm
from ecfutil import CurrencyContext
from tbl import GLACCT, GLSMRZ, EFUSRS, GLSOPT, MSTCMP, CSYFSC, CSYFSP
from tbl import GLYRED, GLALAC, GLSCST, GLSCSI

class JGLS260(JOBEngine):

  def __init__(self, pool):
    super(JGLS260, self).__init__(pool)
    self.session = None
    self.info_dict = {}
    self.ret_earning = {}
    self.ret_earningcl = {}
    self.logger = ecflogger.Logger()

  def verifyYearEnd(self):
    if self.info_dict['glopt'].GLOPCLCD in (None, ''):
      raise Exception('Default closing account has not been setup properly')
    acctid = GLACCT.stripedacct(self.info_dict['glopt'].GLOPCLCD)
    closacct = GLACCT.get((self.info_dict['cono'], acctid))
    if not closacct:
      raise Exception('Default closing account is not found')
    if closacct.GLACACST == 0:
      raise Exception('Default closing account is disabled')
    if closacct.GLACACTP != 'R':
      raise Exception('Default closing account is not on Retained Earnings type')
    self.info_dict['clossing_acct'] = closacct

    #check next fiscal yr
    q = CSYFSC.query
    q = q.filter_by(SYFSFSTP = self.info_dict['fstp'])
    q = q.filter(CSYFSC.SYFSFSYR > self.info_dict['fsyr'])
    nfsyr = q.first()
    if not nfsyr:
      raise Exception('Next fiscal year has not been created')

    self.info_dict['nfsyr'] = nfsyr.SYFSFSYR

  def verifyStructure(self):
    acct_struct = {}
    structs = GLSCST.query.order_by(sa.asc(GLSCST.CSCPCSID)).all()
    for astruct in structs:
      idents = GLSCSI.query.filter_by(CSSICSID = astruct.CSCPCSID).all()
      aidents = {}
      for ident in idents:
        aidents[ident.CSSICSCD] = ident
      acct_struct[astruct.CSCPCSID] = (astruct, aidents)
    self.info_dict['acct_struct'] = acct_struct

  def get_EndBalance(self, smrz):
    dcm.getcontext().prec = 9
    ntret = smrz.GLNTOPBL
    crret = smrz.GLCROPBL
    dbret = smrz.GLDBOPBL
    if ntret == None:
      ntret = dcm.Decimal(0, CurrencyContext)
    if crret == None:
      crret = dcm.Decimal(0, CurrencyContext)
    if dbret == None:
      dbret = dcm.Decimal(0, CurrencyContext)

    for prd in range(15):
      val = getattr(smrz, 'GLNTPR%.2d' % (prd+1), None)
      if val is None:
        val = dcm.Decimal(0, CurrencyContext)
      ntret = dcm.Decimal(ntret + val, CurrencyContext)
      val = getattr(smrz, 'GLCRPR%.2d' % (prd+1), None)
      if val is None:
        val = dcm.Decimal(0, CurrencyContext)
      crret = dcm.Decimal(crret + val, CurrencyContext)
      val = getattr(smrz, 'GLDBPR%.2d' % (prd+1), None)
      if val is None:
        val = dcm.Decimal(0, CurrencyContext)
      dbret = dcm.Decimal(dbret + val, CurrencyContext)

    return (ntret, crret, dbret)

  def do_updateRetEarnItm(self):
    rearnsumrz = {}
    for name, item in self.ret_earningcl.iteritems():
      acctid = GLACCT.stripedacct(name)
      acct = GLACCT.get((self.info_dict['cono'], acctid))
      if not acct:
        raise Exception('Clossing account %s is lost' % acct)

      td = dt.datetime.today()
      # ret earning does not have allocation
      if (acct.GLACALST == 0):
        for curtp, infoitem in item.iteritems():
          smrz = GLSMRZ.get((self.info_dict['cono'], acct.GLACACID, \
                  self.info_dict['fstp'], self.info_dict['fsyr'],
                  1, infoitem[0], infoitem[1]))
          if smrz:
            end_bal = self.get_EndBalance(smrz)
          else:
            dcm.getcontext().prec = 9
            end_bal = (dcm.Decimal(0, CurrencyContext),
                     dcm.Decimal(0, CurrencyContext),
                     dcm.Decimal(0, CurrencyContext))

          if not rearnsumrz.has_key('%s_%s_%s' %
              (acct.GLACACID, infoitem[0], infoitem[1])):
            rearnsumrz['%s_%s_%s' %
              (acct.GLACACID, infoitem[0], infoitem[1])] = [False, None]
          rsmrz = rearnsumrz['%s_%s_%s' %(acct.GLACACID, infoitem[0], infoitem[1])]
          if not rsmrz[1]:
            update_only = True
            nsmrz = GLSMRZ.get((self.info_dict['cono'], acct.GLACACID, \
                    self.info_dict['fstp'], self.info_dict['nfsyr'],
                    1, infoitem[0], infoitem[1]))
            if not nsmrz:
              update_only = False
              nsmrz = GLSMRZ()
              nsmrz.GLSMCONO = self.info_dict['cono']
              nsmrz.GLSMACID = acct.GLACACID
              nsmrz.GLSMFSTP = self.info_dict['fstp']
              nsmrz.GLSMFSYR = self.info_dict['nfsyr']
              nsmrz.GLSMSMTP = 1
              nsmrz.GLSMCUCD = infoitem[0]
              nsmrz.GLSMCUTP = infoitem[1]
              nsmrz.GLNTOPBL = dcm.Decimal(0, CurrencyContext)
              nsmrz.GLCROPBL = dcm.Decimal(0, CurrencyContext)
              nsmrz.GLDBOPBL = dcm.Decimal(0, CurrencyContext)

            rsmrz[0] = update_only
            rsmrz[1] = nsmrz

          nsmrz = rsmrz[1]
          dcm.getcontext().prec = 9
          nsmrz.GLNTOPBL = dcm.Decimal(end_bal[0] + infoitem[3], CurrencyContext)
          nsmrz.GLCROPBL = dcm.Decimal(end_bal[1] + infoitem[4], CurrencyContext)
          nsmrz.GLDBOPBL = dcm.Decimal(end_bal[2] + infoitem[5], CurrencyContext)
          nsmrz.GLSMAUDT = td.date().tointeger()
          nsmrz.GLSMAUTM = td.time().tointeger()
          nsmrz.GLSMAUUS = self.info_dict['usr_info'][3]

      # ret earning does have allocation accounts
      elif (acct.GLACALST == 1):
        alaccts = GLALAC.getObj(True, GLALCONO = acct.GLACCONO, \
          GLALACID = acct.GLACACID)
        for alacct in alaccts:
          _alacct = GLACCT.stripedacct(alacct.GLALALID)
          if not GLACCT.acctexists(acct.GLACCONO, _alacct)[0]:
            raise Exception('Allocation account %s is not found' % alacct.GLALALID)

          for curtp, infoitem in item.iteritems():
            smrz = GLSMRZ.get((self.info_dict['cono'], _alacct, \
                  self.info_dict['fstp'], self.info_dict['fsyr'],
                  1, infoitem[0], infoitem[1]))
            if smrz:
              end_bal = self.get_EndBalance(smrz)
            else:
              dcm.getcontext().prec = 9
              end_bal = (dcm.Decimal(0, CurrencyContext),
                       dcm.Decimal(0, CurrencyContext),
                       dcm.Decimal(0, CurrencyContext))

            if not rearnsumrz.has_key('%s_%s_%s' %
              (_alacct, infoitem[0], infoitem[1])):
              rearnsumrz['%s_%s_%s' %
                (_alacct, infoitem[0], infoitem[1])] = [False, None]
            rsmrz = rearnsumrz['%s_%s_%s' %(_alacct, infoitem[0], infoitem[1])]
            if not rsmrz[1]:
              update_only = True
              nsmrz = GLSMRZ.get((self.info_dict['cono'], _alacct, \
                      self.info_dict['fstp'], self.info_dict['nfsyr'],
                      1, infoitem[0], infoitem[1]))
              if not nsmrz:
                update_only = False
                nsmrz = GLSMRZ()
                nsmrz.GLSMCONO = self.info_dict['cono']
                nsmrz.GLSMACID = _alacct
                nsmrz.GLSMFSTP = self.info_dict['fstp']
                nsmrz.GLSMFSYR = self.info_dict['nfsyr']
                nsmrz.GLSMSMTP = 1
                nsmrz.GLSMCUCD = infoitem[0]
                nsmrz.GLSMCUTP = infoitem[1]
                nsmrz.GLNTOPBL = dcm.Decimal(0, CurrencyContext)
                nsmrz.GLCROPBL = dcm.Decimal(0, CurrencyContext)
                nsmrz.GLDBOPBL = dcm.Decimal(0, CurrencyContext)

              rsmrz[0] = update_only
              rsmrz[1] = nsmrz

            nsmrz = rsmrz[1]
            dcm.getcontext().prec = 9
            alcuam = (dcm.Decimal(infoitem[3]) * dcm.Decimal(alacct.GLALALPC)) / dcm.Decimal(100)
            alcucr = (dcm.Decimal(infoitem[4]) * dcm.Decimal(alacct.GLALALPC)) / dcm.Decimal(100)
            alcudb = (dcm.Decimal(infoitem[5]) * dcm.Decimal(alacct.GLALALPC)) / dcm.Decimal(100)
            nsmrz.GLNTOPBL = dcm.Decimal(end_bal[0] + alcuam, CurrencyContext)
            nsmrz.GLCROPBL = dcm.Decimal(end_bal[1] + alcucr, CurrencyContext)
            nsmrz.GLDBOPBL = dcm.Decimal(end_bal[2] + alcudb, CurrencyContext)
            nsmrz.GLSMAUDT = td.date().tointeger()
            nsmrz.GLSMAUTM = td.time().tointeger()
            nsmrz.GLSMAUUS = self.info_dict['usr_info'][3]

    for name, item in rearnsumrz.iteritems():
      if item[0] == True:
        self.session.update(item[1])
      else:
        self.session.save(item[1])

  def do_updateRetEarning(self):
    acct = self.info_dict['clossing_acct']
    if not acct:
      raise Exception('Clossing account is lost')

    td = dt.datetime.today()
    # ret earning does not have allocation
    if (acct.GLACALST == 0):
      for name, item in self.ret_earning.iteritems():
        smrz = GLSMRZ.get((self.info_dict['cono'], acct.GLACACID, \
                self.info_dict['fstp'], self.info_dict['fsyr'],
                1, item[0], item[1]))
        if smrz:
          end_bal = self.get_EndBalance(smrz)
        else:
          dcm.getcontext().prec = 9
          end_bal = (dcm.Decimal(0, CurrencyContext),
                   dcm.Decimal(0, CurrencyContext),
                   dcm.Decimal(0, CurrencyContext))

        update_only = True
        nsmrz = GLSMRZ.get((self.info_dict['cono'], acct.GLACACID, \
                self.info_dict['fstp'], self.info_dict['nfsyr'],
                1, item[0], item[1]))
        if not nsmrz:
          update_only = False
          nsmrz = GLSMRZ()
          nsmrz.GLSMCONO = self.info_dict['cono']
          nsmrz.GLSMACID = acct.GLACACID
          nsmrz.GLSMFSTP = self.info_dict['fstp']
          nsmrz.GLSMFSYR = self.info_dict['nfsyr']
          nsmrz.GLSMSMTP = 1
          nsmrz.GLSMCUCD = item[0]
          nsmrz.GLSMCUTP = item[1]
          nsmrz.GLNTOPBL = dcm.Decimal(0, CurrencyContext)
          nsmrz.GLCROPBL = dcm.Decimal(0, CurrencyContext)
          nsmrz.GLDBOPBL = dcm.Decimal(0, CurrencyContext)

        dcm.getcontext().prec = 9
        nsmrz.GLNTOPBL = dcm.Decimal(end_bal[0] + item[2], CurrencyContext)
        nsmrz.GLCROPBL = dcm.Decimal(end_bal[1] + item[3], CurrencyContext)
        nsmrz.GLDBOPBL = dcm.Decimal(end_bal[2] + item[4], CurrencyContext)
        nsmrz.GLSMAUDT = td.date().tointeger()
        nsmrz.GLSMAUTM = td.time().tointeger()
        nsmrz.GLSMAUUS = self.info_dict['usr_info'][3]

        if update_only:
          self.session.update(nsmrz)
        else:
          self.session.save(nsmrz)

    # ret earning does have allocation accounts
    elif (acct.GLACALST == 1):
      alaccts = GLALAC.getObj(True, GLALCONO = acct.GLACCONO, \
        GLALACID = acct.GLACACID)
      for alacct in alaccts:
        _alacct = GLACCT.stripedacct(alacct.GLALALID)
        if not GLACCT.acctexists(acct.GLACCONO, _alacct)[0]:
          raise Exception('Allocation account %s is not found' % alacct.GLALALID)

        for name, item in self.ret_earning.iteritems():
          smrz = GLSMRZ.get((self.info_dict['cono'], _alacct, \
                self.info_dict['fstp'], self.info_dict['fsyr'],
                1, item[0], item[1]))
          if smrz:
            end_bal = self.get_EndBalance(smrz)
          else:
            dcm.getcontext().prec = 9
            end_bal = (dcm.Decimal(0, CurrencyContext),
                     dcm.Decimal(0, CurrencyContext),
                     dcm.Decimal(0, CurrencyContext))

          update_only = True
          nsmrz = GLSMRZ.get((self.info_dict['cono'], _alacct, \
                  self.info_dict['fstp'], self.info_dict['nfsyr'],
                  1, item[0], item[1]))
          if not nsmrz:
            update_only = False
            nsmrz = GLSMRZ()
            nsmrz.GLSMCONO = self.info_dict['cono']
            nsmrz.GLSMACID = _alacct
            nsmrz.GLSMFSTP = self.info_dict['fstp']
            nsmrz.GLSMFSYR = self.info_dict['nfsyr']
            nsmrz.GLSMSMTP = 1
            nsmrz.GLSMCUCD = item[0]
            nsmrz.GLSMCUTP = item[1]
            nsmrz.GLNTOPBL = dcm.Decimal(0, CurrencyContext)
            nsmrz.GLCROPBL = dcm.Decimal(0, CurrencyContext)
            nsmrz.GLDBOPBL = dcm.Decimal(0, CurrencyContext)

          dcm.getcontext().prec = 9
          alcuam = (dcm.Decimal(item[2]) * dcm.Decimal(alacct.GLALALPC)) / dcm.Decimal(100)
          alcucr = (dcm.Decimal(item[3]) * dcm.Decimal(alacct.GLALALPC)) / dcm.Decimal(100)
          alcudb = (dcm.Decimal(item[4]) * dcm.Decimal(alacct.GLALALPC)) / dcm.Decimal(100)
          nsmrz.GLNTOPBL = dcm.Decimal(end_bal[0] + alcuam, CurrencyContext)
          nsmrz.GLCROPBL = dcm.Decimal(end_bal[1] + alcucr, CurrencyContext)
          nsmrz.GLDBOPBL = dcm.Decimal(end_bal[2] + alcudb, CurrencyContext)
          nsmrz.GLSMAUDT = td.date().tointeger()
          nsmrz.GLSMAUTM = td.time().tointeger()
          nsmrz.GLSMAUUS = self.info_dict['usr_info'][3]

          if update_only:
            self.session.update(nsmrz)
          else:
            self.session.save(nsmrz)

  def do_YearEndSmrz(self, acct, smrz):
    #if income statement
    td = dt.datetime.today()
    if acct.GLACACTP == 'I':
      end_bal = self.get_EndBalance(smrz)

      use_default = True
      acct_struct = self.info_dict['acct_struct']
      for idcode in range(10):
        acctcode = getattr(acct, 'GLACCS%.2d' % (idcode + 1), None)
        if (acctcode not in (None, '')) and acct_struct.has_key(idcode + 1):
          struct = acct_struct[idcode + 1]
          if (struct[0].CSCPCSCL == 1) and (struct[1].has_key(acctcode)):
            clobj = struct[1][acctcode]
            if clobj.CSSICUCD not in (None, ''):
              use_default = False
              if not self.ret_earningcl.has_key(clobj.CSSICUCD):
                self.ret_earningcl[clobj.CSSICUCD] = {}
              reitm = self.ret_earningcl[clobj.CSSICUCD]
              if not reitm.has_key('%s-%s' % (smrz.GLSMCUCD, smrz.GLSMCUTP)):
                reitm['%s-%s' % (smrz.GLSMCUCD, smrz.GLSMCUTP)] = \
                  [smrz.GLSMCUCD, smrz.GLSMCUTP, clobj.CSSICUCD,
                  dcm.Decimal(0, CurrencyContext), # NET
                  dcm.Decimal(0, CurrencyContext), # CR
                  dcm.Decimal(0, CurrencyContext)] # DB
              earning = reitm['%s-%s' % (smrz.GLSMCUCD, smrz.GLSMCUTP)]
              earning[3] = dcm.Decimal(earning[3] + end_bal[0], CurrencyContext) # NET
              earning[4] = dcm.Decimal(earning[4] + end_bal[1], CurrencyContext) # CR
              earning[5] = dcm.Decimal(earning[5] + end_bal[2], CurrencyContext) # DB

      if use_default:
        dcm.getcontext().prec = 9
        if not self.ret_earning.has_key('%s-%s' % (smrz.GLSMCUCD, smrz.GLSMCUTP)):
          self.ret_earning['%s-%s' % (smrz.GLSMCUCD, smrz.GLSMCUTP)] = \
            [smrz.GLSMCUCD, smrz.GLSMCUTP,
             dcm.Decimal(0, CurrencyContext), # NET
             dcm.Decimal(0, CurrencyContext), # CR
             dcm.Decimal(0, CurrencyContext)] # DB
        earning = self.ret_earning['%s-%s' % (smrz.GLSMCUCD, smrz.GLSMCUTP)]
        earning[2] = dcm.Decimal(earning[2] + end_bal[0], CurrencyContext) # NET
        earning[3] = dcm.Decimal(earning[3] + end_bal[1], CurrencyContext) # CR
        earning[4] = dcm.Decimal(earning[4] + end_bal[2], CurrencyContext) # DB

      nsmrz = GLSMRZ.get((smrz.GLSMCONO, smrz.GLSMACID, smrz.GLSMFSTP, \
                self.info_dict['nfsyr'], smrz.GLSMSMTP, smrz.GLSMCUCD,
                smrz.GLSMCUTP))

      update_only = True
      if not nsmrz:
        update_only = False
        nsmrz = GLSMRZ()
        nsmrz.GLSMCONO = smrz.GLSMCONO
        nsmrz.GLSMACID = smrz.GLSMACID
        nsmrz.GLSMFSTP = smrz.GLSMFSTP
        nsmrz.GLSMFSYR = self.info_dict['nfsyr']
        nsmrz.GLSMSMTP = smrz.GLSMSMTP
        nsmrz.GLSMCUCD = smrz.GLSMCUCD
        nsmrz.GLSMCUTP = smrz.GLSMCUTP

      dcm.getcontext().prec = 9
      nsmrz.GLNTOPBL = dcm.Decimal(0, CurrencyContext)
      nsmrz.GLCROPBL = dcm.Decimal(0, CurrencyContext)
      nsmrz.GLDBOPBL = dcm.Decimal(0, CurrencyContext)
      nsmrz.GLSMAUDT = td.date().tointeger()
      nsmrz.GLSMAUTM = td.time().tointeger()
      nsmrz.GLSMAUUS = self.info_dict['usr_info'][3]

      if update_only:
        self.session.update(nsmrz)
      else:
        self.session.save(nsmrz)

    elif acct.GLACACTP in ('B', 'R'):
      end_bal = self.get_EndBalance(smrz)
      dcm.getcontext().prec = 9
      nsmrz = GLSMRZ.get((smrz.GLSMCONO, smrz.GLSMACID, smrz.GLSMFSTP, \
                self.info_dict['nfsyr'], smrz.GLSMSMTP, smrz.GLSMCUCD,
                smrz.GLSMCUTP))
      update_only = True
      if not nsmrz:
        update_only = False
        nsmrz = GLSMRZ()
        nsmrz.GLSMCONO = smrz.GLSMCONO
        nsmrz.GLSMACID = smrz.GLSMACID
        nsmrz.GLSMFSTP = smrz.GLSMFSTP
        nsmrz.GLSMFSYR = self.info_dict['nfsyr']
        nsmrz.GLSMSMTP = smrz.GLSMSMTP
        nsmrz.GLSMCUCD = smrz.GLSMCUCD
        nsmrz.GLSMCUTP = smrz.GLSMCUTP

      dcm.getcontext().prec = 9
      nsmrz.GLNTOPBL = dcm.Decimal(end_bal[0], CurrencyContext)
      nsmrz.GLCROPBL = dcm.Decimal(end_bal[1], CurrencyContext)
      nsmrz.GLDBOPBL = dcm.Decimal(end_bal[2], CurrencyContext)
      nsmrz.GLSMAUDT = td.date().tointeger()
      nsmrz.GLSMAUTM = td.time().tointeger()
      nsmrz.GLSMAUUS = self.info_dict['usr_info'][3]

      if update_only:
        self.session.update(nsmrz)
      else:
        self.session.save(nsmrz)

  def do_YearEndAcct(self, acct):
    q = GLSMRZ.query
    q = q.filter_by(GLSMCONO = self.info_dict['cono'])
    q = q.filter_by(GLSMACID = acct.GLACACID)
    q = q.filter_by(GLSMFSTP = self.info_dict['fstp'])
    q = q.filter_by(GLSMFSYR = self.info_dict['fsyr'])
    q = q.filter_by(GLSMSMTP = 1) # non-provisional summary
    q = q.order_by(sa.asc(GLSMRZ.GLSMCONO))
    q = q.order_by(sa.asc(GLSMRZ.GLSMACID))
    q = q.order_by(sa.asc(GLSMRZ.GLSMFSTP))
    q = q.order_by(sa.asc(GLSMRZ.GLSMFSYR))
    q = q.order_by(sa.asc(GLSMRZ.GLSMSMTP))
    q = q.order_by(sa.asc(GLSMRZ.GLSMCUCD))
    q = q.order_by(sa.asc(GLSMRZ.GLSMCUTP))
    smrzs = q.all()
    for smrz in smrzs:
      self.do_YearEndSmrz(acct, smrz)

  def do_YearEnd(self):
    self.logger.notifyChannel('init', ecflogger.LOG_INFO, 'Initializing year end closing - %d' % (self.info_dict['fsyr']))
    self.verifyYearEnd()
    self.verifyStructure()

    q = GLACCT.query
    q = q.filter_by(GLACCONO = self.info_dict['cono'])
    q = q.filter_by(GLACACST = 1)
    q = q.order_by(sa.asc(GLACCT.GLACCONO))
    q = q.order_by(sa.asc(GLACCT.GLACACID))
    accts = q.all()

    self.logger.notifyChannel('init', ecflogger.LOG_INFO, 'Processing year end closing - %d' % (self.info_dict['fsyr']))
    if not self.session.transaction_started():
      self.session.begin()
    try:
      for acct in accts:
        self.do_YearEndAcct(acct)
      self.session.commit()
    except:
      self.session.rollback()
      self.session.clear()
      raise

    self.logger.notifyChannel('init', ecflogger.LOG_INFO, 'Adjusting retained earnings')
    if not self.session.transaction_started():
      self.session.begin()
    try:
      self.do_updateRetEarnItm()
      self.do_updateRetEarning()
      self.session.commit()
    except:
      self.session.rollback()
      self.session.clear()
      raise

  def execYearEnd(self, fstp, fsyr, usr_name):
    proxy = self.getBusinessObjectProxy()
    usrobj = proxy.getObject('USROBJ')
    glsobj = proxy.getObject('GLSOBJ')
    info = usrobj.getUserInfoEx(job.usr_name)
    cono = info[2]

    mstcmp = MSTCMP.get(cono)
    glopt  = GLSOPT.get(cono)

    self.info_dict['fstp'] = fstp
    self.info_dict['fsyr'] = fsyr
    self.info_dict['cono'] = cono
    self.info_dict['usr_info'] = info
    self.info_dict['cmp'] = mstcmp
    self.info_dict['glopt'] = glopt
    self.session = session

    self.do_YearEnd()

  def executeJob(self, jobsession):
    job = GLYRED.get(jobsession.jobID)
    if not job:
      raise Exception('Job information could not be found')

    proxy = self.getBusinessObjectProxy()
    usrobj = proxy.getObject('USROBJ')
    glsobj = proxy.getObject('GLSOBJ')
    info = usrobj.getUserInfoEx(job.GLYRAUUS)
    cono = info[2]

    mstcmp = MSTCMP.get(cono)
    glopt  = GLSOPT.get(cono)

    self.info_dict['fstp'] = job.GLYRFSTP
    self.info_dict['fsyr'] = job.GLYRFSYR
    self.info_dict['cono'] = cono
    self.info_dict['usr_info'] = info
    self.info_dict['cmp'] = mstcmp
    self.info_dict['glopt'] = glopt
    self.info_dict['jobsession'] = jobsession
    self.info_dict['job'] = job
    self.session = session

    self.do_YearEnd()




