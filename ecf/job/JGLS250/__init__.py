from elixir import *
from jobsvc import *
import ecflogger
import datetime as dt
from sqlalchemy import sql
from sqlalchemy.sql import operators
from sqlalchemy.orm.attributes import InstrumentedAttribute
import sqlalchemy as sa
import decimal as dcm
from ecfutil import CurrencyContext
from tbl import GLPOST, EFUSRS, GLSOPT, MSTCMP, GLACCT, GLALAC
from tbl import GLBCNO, GLBCTL, GLJHDR, GLJITM, GLSMRZ, GLHIST
from tbl import CSYSYS, MSTCUR, CSYFSP

class EPostingError(Exception):
  """Posting transaction exception"""

class JGLS250(JOBEngine):

  def __init__(self, pool):
    super(JGLS250, self).__init__(pool)
    self.session = None
    self.info_dict = {}
    self.prvfsyr = []
    self.logger = ecflogger.Logger()

  def do_validateAcct(self, jitm):
    acctid = GLACCT.get((jitm.GLJICONO, jitm.GLJIACID))
    if (not acctid) or (acctid.GLACACST == 0):
      raise Exception('Account ID id not found or disabled')
    dcm.getcontext().prec = 9
    if (acctid.GLACALST == 1) and \
       (dcm.Decimal(acctid.GLACALPC, CurrencyContext) != dcm.Decimal(100, CurrencyContext)):
      raise Exception('Allocation account is empty, could not post')
    return acctid

  def do_validateCurrency(self, cucd):
    cucd = MSTCUR.get(cucd)
    if not cucd:
      raise Exception('Currency code does not exist')
    return cucd

  def delProvSumrz(self, jhdr, fsyr):
    q = GLSMRZ.query
    q = q.filter_by(GLSMCONO = jhdr.GLJHCONO)
    q = q.filter_by(GLSMFSTP = self.info_dict['glopt'].GLOPFSTP)
    q = q.filter_by(GLSMFSYR = fsyr)
    q = q.filter_by(GLSMSMTP = 2)
    objs = q.all()
    if not self.session.transaction_started():
      self.session.begin()
    try:
      for obj in objs:
        self.session.delete(obj)
      self.session.commit()
    except:
      self.session.clear()
      self.session.rollback()
      raise

  def copyProvSumrz(self, jhdr, fsyr):
    q = GLSMRZ.query
    q = q.filter_by(GLSMCONO = jhdr.GLJHCONO)
    q = q.filter_by(GLSMFSTP = self.info_dict['glopt'].GLOPFSTP)
    q = q.filter_by(GLSMFSYR = fsyr)
    q = q.filter_by(GLSMSMTP = 1)
    objs = q.all()

    td = dt.datetime.now()
    if not self.session.transaction_started():
      self.session.begin()
    try:
      for obj in objs:
        psmrz = GLSMRZ(
              GLSMAUDT = td.date().tointeger(),
              GLSMAUTM = td.time().tointeger(),
              GLSMAUUS = self.info_dict['usr_info'][3])
        for key in GLSMRZ.__dict__.iterkeys():
          if isinstance(GLSMRZ.__dict__[key], InstrumentedAttribute):
            val = getattr(obj, key, None)
            setattr(psmrz, key, val)

        psmrz.GLSMSMTP = 2
        psmrz.GLSMAUDT = td.date().tointeger()
        psmrz.GLSMAUTM = td.time().tointeger()
        psmrz.GLSMAUUS = self.info_dict['usr_info'][3]
        self.session.save(psmrz)

      self.session.commit()
    except:
      self.session.clear()
      self.session.rollback()
      raise

  def prepProvSumrz(self, jhdr, fsyr):
    if fsyr not in self.prvfsyr:
      self.delProvSumrz(jhdr, fsyr)
      self.copyProvSumrz(jhdr, fsyr)
      self.prvfsyr.append(fsyr)

  def do_moveErrorJV(self, bctl, jhdr):
    td = dt.datetime.now()
    batch = self.info_dict['err_batch']
    if batch == None:
      lsno = GLBCNO.getLSNO(jhdr.GLJHNOID)
      batch = GLBCTL()
      for key in GLBCTL.__dict__.iterkeys():
        if isinstance(GLBCTL.__dict__[key], InstrumentedAttribute):
          val = getattr(bctl, key, None)
          setattr(batch, key, val)
      batch.GLBCLSID  = lsno
      batch.GLBCNODS  = 'Error Batch'
      batch.GLBCLSTR  = 0
      batch.GLBCCTTR  = 0
      batch.GLBCCTER  = 0
      batch.GLBCNTDB  = 0
      batch.GLBCNTCR  = 0
      batch.GLBCPRST  = 0
      batch.GLBCBCST  = 5
      batch.GLBCAUDT  = td.date().tointeger()
      batch.GLBCAUTM  = td.time().tointeger()
      batch.GLBCAUUS  = self.info_dict['usr_info'][3]
      if not self.session.transaction_started():
        self.session.begin()
      try:
        self.session.save(batch)
        self.session.commit()
        self.info_dict['err_batch'] = batch
      except:
        self.session.rollback()
        self.session.clear()

    if not self.session.transaction_started():
      self.session.begin()
    try:
      jlsno = GLJHDR.getLSNO(batch)
      hdr = GLJHDR()
      for key in GLJHDR.__dict__.iterkeys():
        if isinstance(GLJHDR.__dict__[key], InstrumentedAttribute):
          val = getattr(jhdr, key, None)
          setattr(hdr, key, val)

      hdr.GLJHBCID = batch.GLBCLSID
      hdr.GLJHJEID = jlsno[0]
      hdr.GLJHAUDT = td.date().tointeger()
      hdr.GLJHAUTM = td.time().tointeger()
      hdr.GLJHAUUS = self.info_dict['usr_info'][3]

      q = GLJITM.query
      q = q.filter_by(GLJICONO = jhdr.GLJHCONO)
      q = q.filter_by(GLJINOID = jhdr.GLJHNOID)
      q = q.filter_by(GLJIBCID = jhdr.GLJHBCID)
      q = q.filter_by(GLJIJEID = jhdr.GLJHJEID)
      q = q.order_by(sa.asc(GLJITM.GLJICONO))
      q = q.order_by(sa.asc(GLJITM.GLJINOID))
      q = q.order_by(sa.asc(GLJITM.GLJIBCID))
      q = q.order_by(sa.asc(GLJITM.GLJIJEID))
      q = q.order_by(sa.asc(GLJITM.GLJISQNO))
      jitms = q.all()

      for jitm in jitms:
        itm = GLJITM()
        for key in GLJITM.__dict__.iterkeys():
          if isinstance(GLJITM.__dict__[key], InstrumentedAttribute):
            val = getattr(jitm, key, None)
            setattr(itm, key, val)

        itm.GLJIBCID = batch.GLBCLSID
        itm.GLJIJEID = hdr.GLJHJEID
        itm.GLJIAUDT = td.date().tointeger()
        itm.GLJIAUTM = td.time().tointeger()
        itm.GLJIAUUS = self.info_dict['usr_info'][3]

        for key in GLJITM.__dict__.iterkeys():
          if isinstance(GLJITM.__dict__[key], InstrumentedAttribute):
            val = getattr(itm, key, None)
            print (key, val)

        self.session.delete(jitm)
        self.session.save(itm)

      dcm.getcontext().prec = 9
      bctl.GLBCNTDB = dcm.Decimal(bctl.GLBCNTDB, CurrencyContext) - jhdr.GLJHNTDB
      bctl.GLBCNTCR = dcm.Decimal(bctl.GLBCNTCR, CurrencyContext) - jhdr.GLJHNTCR

      self.session.delete(jhdr)
      self.session.update(bctl)

      batch.GLBCNTDB = dcm.Decimal(batch.GLBCNTDB, CurrencyContext) + hdr.GLJHNTDB
      batch.GLBCNTCR = dcm.Decimal(batch.GLBCNTCR, CurrencyContext) + hdr.GLJHNTCR

      self.session.update(batch)
      self.session.save(hdr)
      self.session.commit()
    except:
      self.session.rollback()
      self.session.clear()
      raise

  def do_postJV(self, bctl, jhdr):
    if not self.session.transaction_started():
      self.session.begin()
    try:
      if ((jhdr.GLJHNTDB in (None, 0)) and \
         (jhdr.GLJHNTCR in (None, 0))) or \
         (jhdr.GLJHNTDB != jhdr.GLJHNTCR):
        raise EPostingError('Journal is empty or not balanced')
      self.logger.notifyChannel('proc', ecflogger.LOG_INFO, 'Processing journal %.6d' % (jhdr.GLJHJEID))
      q = GLJITM.query
      q = q.filter_by(GLJICONO = jhdr.GLJHCONO)
      q = q.filter_by(GLJINOID = jhdr.GLJHNOID)
      q = q.filter_by(GLJIBCID = jhdr.GLJHBCID)
      q = q.filter_by(GLJIJEID = jhdr.GLJHJEID)
      q = q.order_by(sa.asc(GLJITM.GLJICONO))
      q = q.order_by(sa.asc(GLJITM.GLJINOID))
      q = q.order_by(sa.asc(GLJITM.GLJIBCID))
      q = q.order_by(sa.asc(GLJITM.GLJIJEID))
      q = q.order_by(sa.asc(GLJITM.GLJISQNO))
      jitms = q.all()
      td = dt.datetime.now()
      info = self.info_dict['usr_info']
      idno = 0
      for jitm in jitms:
        self.logger.notifyChannel('proc', ecflogger.LOG_INFO, 'START:posting transaction %s' % jitm.GLJIACFM)
        acctid = self.do_validateAcct(jitm)
        fcucd = self.do_validateCurrency(jitm.GLJICSCD)
        scucd = self.do_validateCurrency(jitm.GLJICHCD)

        # Only create GL History on normal post
        if self.info_dict['job'].GLPOPOTP == 1:
          if idno < 1:
            idno = GLHIST.getLastIDNO(jhdr.GLJHCONO, \
              self.info_dict['glopt'].GLOPFSTP, jhdr.GLJHFSYR)
          else:
            idno += 1
          self.logger.notifyChannel('proc', ecflogger.LOG_INFO, 'creating transaction history')
          histitm = GLHIST(
              GLHIAUDT = td.date().tointeger(),
              GLHIAUTM = td.time().tointeger(),
              GLHIAUUS = self.info_dict['usr_info'][3]
            )
          histitm.GLHICONO = jhdr.GLJHCONO
          histitm.GLHIFSTP = self.info_dict['glopt'].GLOPFSTP
          histitm.GLHIFSYR = jhdr.GLJHFSYR
          histitm.GLHIIDNO = idno
          histitm.GLHIFSPR = jhdr.GLJHFSPR
          histitm.GLHIJEDT = jhdr.GLJHJEDT
          histitm.GLHIJEDS = jhdr.GLJHJEDS
          histitm.GLHIHSSR = jhdr.GLJHSRLG
          histitm.GLHIHSTP = jhdr.GLJHSRTP
          histitm.GLHITRDT = jitm.GLJITRDT
          histitm.GLHITRDS = jitm.GLJITRDS
          histitm.GLHITRRF = jitm.GLJITRRF
          histitm.GLHITRDT = jitm.GLJITRDT
          histitm.GLHIACID = jitm.GLJIACID
          histitm.GLHIACFM = jitm.GLJIACFM
          histitm.GLHIACNM = jitm.GLJIACNM
          histitm.GLHISRLG = jitm.GLJISRLG
          histitm.GLHISRTP = jitm.GLJISRTP
          histitm.GLHITRAM = jitm.GLJITRAM
          histitm.GLHITRDB = jitm.GLJITRDB
          histitm.GLHITRCR = jitm.GLJITRCR
          histitm.GLHITRTP = jitm.GLJITRTP
          histitm.GLHICUDC = jitm.GLJICUDC
          histitm.GLHICHCD = jitm.GLJICHCD
          histitm.GLHICRTP = jitm.GLJICRTP
          histitm.GLHIDTMT = jitm.GLJIDTMT
          histitm.GLHIRTOP = jitm.GLJIRTOP
          histitm.GLHIRTDT = jitm.GLJIRTDT
          histitm.GLHIRTVL = jitm.GLJIRTVL
          histitm.GLHIRTSP = jitm.GLJIRTSP
          histitm.GLHICSCD = jitm.GLJICSCD
          histitm.GLHICUAM = jitm.GLJICUAM
          histitm.GLHICUDB = jitm.GLJICUDB
          histitm.GLHICUCR = jitm.GLJICUCR
          histitm.GLHINOID = jitm.GLJINOID
          histitm.GLHIBCID = jitm.GLJIBCID
          histitm.GLHIJEID = jitm.GLJIJEID
          histitm.GLHITRID = jitm.GLJITRID
          session.save(histitm)
          if (jhdr.GLJHJERV == 1):
            self.logger.notifyChannel('proc', ecflogger.LOG_INFO, 'creating reversal history')
            nxtprd = CSYFSP.getNextPeriod(self.info_dict['glopt'].GLOPFSTP, \
              jhdr.GLJHFSYR, jhdr.GLJHFSPR)
            if not nxtprd:
              raise EPostingError('No appropriate fiscal period to post reversal journal')

            idno += 1
            histrv = GLHIST(
              GLHIAUDT = td.date().tointeger(),
              GLHIAUTM = td.time().tointeger(),
              GLHIAUUS = self.info_dict['usr_info'][3]
            )
            if jitm.GLJITRTP == 1:
              trtp = 2
            else:
              trtp = 1
            dcm.getcontext().prec = 9
            amount  = dcm.Decimal(jitm.GLJITRAM * dcm.Decimal(-1, CurrencyContext), CurrencyContext)
            namount = dcm.Decimal(jitm.GLJICUAM * dcm.Decimal(-1, CurrencyContext), CurrencyContext)
            histrv.GLHICONO = jhdr.GLJHCONO
            histrv.GLHIFSTP = self.info_dict['glopt'].GLOPFSTP
            histrv.GLHIFSYR = nxtprd[0]
            histrv.GLHIIDNO = idno
            histrv.GLHIFSPR = nxtprd[1]
            histrv.GLHIJEDT = jhdr.GLJHJEDT
            histrv.GLHIJEDS = jhdr.GLJHJEDS
            histrv.GLHIHSSR = jhdr.GLJHSRLG
            histrv.GLHIHSTP = jhdr.GLJHSRTP
            histrv.GLHITRDT = jitm.GLJITRDT
            histrv.GLHITRDS = jitm.GLJITRDS
            histrv.GLHITRRF = jitm.GLJITRRF
            histrv.GLHITRDT = jitm.GLJITRDT
            histrv.GLHIACID = jitm.GLJIACID
            histrv.GLHIACFM = jitm.GLJIACFM
            histrv.GLHIACNM = jitm.GLJIACNM
            histrv.GLHISRLG = jitm.GLJISRLG
            histrv.GLHISRTP = jitm.GLJISRTP
            histrv.GLHITRAM = amount
            histrv.GLHITRDB = jitm.GLJITRCR
            histrv.GLHITRCR = jitm.GLJITRDB
            histrv.GLHITRTP = trtp
            histrv.GLHICUDC = jitm.GLJICUDC
            histrv.GLHICHCD = jitm.GLJICHCD
            histrv.GLHICRTP = jitm.GLJICRTP
            histrv.GLHIDTMT = jitm.GLJIDTMT
            histrv.GLHIRTOP = jitm.GLJIRTOP
            histrv.GLHIRTDT = jitm.GLJIRTDT
            histrv.GLHIRTVL = jitm.GLJIRTVL
            histrv.GLHIRTSP = jitm.GLJIRTSP
            histrv.GLHICSCD = jitm.GLJICSCD
            histrv.GLHICUAM = namount
            histrv.GLHICUDB = jitm.GLJICUDB
            histrv.GLHICUCR = jitm.GLJICUCR
            histrv.GLHINOID = jitm.GLJINOID
            histrv.GLHIBCID = jitm.GLJIBCID
            histrv.GLHIJEID = jitm.GLJIJEID
            histrv.GLHITRID = jitm.GLJITRID
            session.save(histrv)

        # normal account posting procedures
        if acctid.GLACALST in (None, 0):
          # provisional posting
          if self.info_dict['job'].GLPOPOTP == 2:
            self.logger.notifyChannel('proc', ecflogger.LOG_INFO, 'creating provisional summary')
            psmrzitm = GLSMRZ.get((jhdr.GLJHCONO, jitm.GLJIACID, \
              self.info_dict['glopt'].GLOPFSTP, jhdr.GLJHFSYR, \
              2, jitm.GLJICSCD, 'F'))
            insmode = False
            self.logger.notifyChannel('proc', ecflogger.LOG_INFO, 'adjusting functional currency summary')
            if not psmrzitm:
              insmode = True
              psmrzitm = GLSMRZ(
                GLSMCONO = jhdr.GLJHCONO,
                GLSMACID = jitm.GLJIACID,
                GLSMFSTP = self.info_dict['glopt'].GLOPFSTP,
                GLSMFSYR = jhdr.GLJHFSYR,
                GLSMSMTP = 2,
                GLSMCUCD = jitm.GLJICSCD,
                GLSMCUTP = 'F',
                GLSMAUDT = td.date().tointeger(),
                GLSMAUTM = td.time().tointeger(),
                GLSMAUUS = self.info_dict['usr_info'][3])
            ntfldnm = 'GLNTPR%.2d' % jhdr.GLJHFSPR
            crfldnm = 'GLCRPR%.2d' % jhdr.GLJHFSPR
            dbfldnm = 'GLDBPR%.2d' % jhdr.GLJHFSPR

            dcm.getcontext().prec = 9
            val = getattr(psmrzitm, ntfldnm, None)
            if val is None:
              val = dcm.Decimal(0, CurrencyContext)
            setattr(psmrzitm, ntfldnm, dcm.Decimal(val + jitm.GLJICUAM, CurrencyContext))

            val = getattr(psmrzitm, crfldnm, None)
            if val is None:
              val = dcm.Decimal(0, CurrencyContext)
            setattr(psmrzitm, crfldnm, dcm.Decimal(val + jitm.GLJICUCR, CurrencyContext))

            val = getattr(psmrzitm, dbfldnm, None)
            if val is None:
              val = dcm.Decimal(0, CurrencyContext)
            setattr(psmrzitm, dbfldnm, dcm.Decimal(val + jitm.GLJICUDB, CurrencyContext))

            psmrzitm.GLSMAUDT = td.date().tointeger()
            psmrzitm.GLSMAUTM = td.time().tointeger()
            psmrzitm.GLSMAUUS = self.info_dict['usr_info'][3]

            if insmode:
              self.session.save(psmrzitm)
            else:
              self.session.update(psmrzitm)

            if jitm.GLJICSCD != jitm.GLJICHCD:
              self.logger.notifyChannel('proc', ecflogger.LOG_INFO, 'adjusting source currency summary')
              pcsmrzitm = GLSMRZ.get((jhdr.GLJHCONO, jitm.GLJIACID, \
                self.info_dict['glopt'].GLOPFSTP, jhdr.GLJHFSYR, \
                2, jitm.GLJICHCD, 'S'))
              insmode = False
              if not pcsmrzitm:
                insmode = True
                pcsmrzitm = GLSMRZ(
                  GLSMCONO = jhdr.GLJHCONO,
                  GLSMACID = jitm.GLJIACID,
                  GLSMFSTP = self.info_dict['glopt'].GLOPFSTP,
                  GLSMFSYR = jhdr.GLJHFSYR,
                  GLSMSMTP = 2,
                  GLSMCUCD = jitm.GLJICHCD,
                  GLSMCUTP = 'S',
                  GLSMAUDT = td.date().tointeger(),
                  GLSMAUTM = td.time().tointeger(),
                  GLSMAUUS = self.info_dict['usr_info'][3])
              ntfldnm = 'GLNTPR%.2d' % jhdr.GLJHFSPR
              crfldnm = 'GLCRPR%.2d' % jhdr.GLJHFSPR
              dbfldnm = 'GLDBPR%.2d' % jhdr.GLJHFSPR

              dcm.getcontext().prec = 9
              val = getattr(pcsmrzitm, ntfldnm, None)
              if val is None:
                val = dcm.Decimal(0, CurrencyContext)
              setattr(pcsmrzitm, ntfldnm, dcm.Decimal(val + jitm.GLJITRAM, CurrencyContext))

              val = getattr(pcsmrzitm, crfldnm, None)
              if val is None:
                val = dcm.Decimal(0, CurrencyContext)
              setattr(pcsmrzitm, crfldnm, dcm.Decimal(val + jitm.GLJITRCR, CurrencyContext))

              val = getattr(pcsmrzitm, dbfldnm, None)
              if val is None:
                val = dcm.Decimal(0, CurrencyContext)
              setattr(pcsmrzitm, dbfldnm, dcm.Decimal(val + jitm.GLJITRDB, CurrencyContext))

              pcsmrzitm.GLSMAUDT = td.date().tointeger()
              pcsmrzitm.GLSMAUTM = td.time().tointeger()
              pcsmrzitm.GLSMAUUS = self.info_dict['usr_info'][3]

              if insmode:
                self.session.save(pcsmrzitm)
              else:
                self.session.update(pcsmrzitm)

            if (jhdr.GLJHJERV == 1):
              self.logger.notifyChannel('proc', ecflogger.LOG_INFO, 'adjusting reversal summary')
              nxtprd = CSYFSP.getNextPeriod(self.info_dict['glopt'].GLOPFSTP, \
                jhdr.GLJHFSYR, jhdr.GLJHFSPR)
              if not nxtprd:
                raise EPostingError('No appropriate fiscal period to post reversal journal')

              if nxtprd[0] != psmrzitm.GLSMFSYR:
                psmrzitm = GLSMRZ.get((jhdr.GLJHCONO, jitm.GLJIACID, \
                  self.info_dict['glopt'].GLOPFSTP, jhdr.GLJHFSYR, \
                  2, jitm.GLJICSCD, 'F'))

              insmode = False
              if not psmrzitm:
                insmode = True
                psmrzitm = GLSMRZ(
                  GLSMCONO = jhdr.GLJHCONO,
                  GLSMACID = jitm.GLJIACID,
                  GLSMFSTP = self.info_dict['glopt'].GLOPFSTP,
                  GLSMFSYR = nxtprd[0],
                  GLSMSMTP = 2,
                  GLSMCUCD = jitm.GLJICSCD,
                  GLSMCUTP = 'F',
                  GLSMAUDT = td.date().tointeger(),
                  GLSMAUTM = td.time().tointeger(),
                  GLSMAUUS = self.info_dict['usr_info'][3])

              ntfldnm = 'GLNTPR%.2d' % nxtprd[1]
              crfldnm = 'GLCRPR%.2d' % nxtprd[1]
              dbfldnm = 'GLDBPR%.2d' % nxtprd[1]

              dcm.getcontext().prec = 9
              namount = dcm.Decimal(jitm.GLJICUAM * dcm.Decimal(-1, CurrencyContext), CurrencyContext)
              val = getattr(psmrzitm, ntfldnm, None)
              if val is None:
                val = dcm.Decimal(0, CurrencyContext)
              setattr(psmrzitm, ntfldnm, dcm.Decimal(val + namount, CurrencyContext))

              val = getattr(psmrzitm, crfldnm, None)
              if val is None:
                val = dcm.Decimal(0, CurrencyContext)
              setattr(psmrzitm, crfldnm, dcm.Decimal(val + jitm.GLJICUDB, CurrencyContext))

              val = getattr(psmrzitm, dbfldnm, None)
              if val is None:
                val = dcm.Decimal(0, CurrencyContext)
              setattr(psmrzitm, dbfldnm, dcm.Decimal(val + jitm.GLJICUCR, CurrencyContext))

              psmrzitm.GLSMAUDT = td.date().tointeger()
              psmrzitm.GLSMAUTM = td.time().tointeger()
              psmrzitm.GLSMAUUS = self.info_dict['usr_info'][3]

              if insmode:
                self.session.save(psmrzitm)
              else:
                self.session.update(psmrzitm)

              if jitm.GLJICSCD != jitm.GLJICHCD:

                if nxtprd[0] != pcsmrzitm.GLSMFSYR:
                  pcsmrzitm = GLSMRZ.get((jhdr.GLJHCONO, jitm.GLJIACID, \
                    self.info_dict['glopt'].GLOPFSTP, nxtprd[0], \
                    2, jitm.GLJICHCD, 'S'))

                insmode = False
                if not pcsmrzitm:
                  insmode = True
                  pcsmrzitm = GLSMRZ(
                    GLSMCONO = jhdr.GLJHCONO,
                    GLSMACID = jitm.GLJIACID,
                    GLSMFSTP = self.info_dict['glopt'].GLOPFSTP,
                    GLSMFSYR = nxtprd[0],
                    GLSMSMTP = 2,
                    GLSMCUCD = jitm.GLJICHCD,
                    GLSMCUTP = 'S',
                    GLSMAUDT = td.date().tointeger(),
                    GLSMAUTM = td.time().tointeger(),
                    GLSMAUUS = self.info_dict['usr_info'][3])

                ntfldnm = 'GLNTPR%.2d' % nxtprd[1]
                crfldnm = 'GLCRPR%.2d' % nxtprd[1]
                dbfldnm = 'GLDBPR%.2d' % nxtprd[1]

                dcm.getcontext().prec = 9
                amount = dcm.Decimal(jitm.GLJITRAM * dcm.Decimal(-1, CurrencyContext), CurrencyContext)
                val = getattr(pcsmrzitm, ntfldnm, None)
                if val is None:
                  val = dcm.Decimal(0, CurrencyContext)
                setattr(pcsmrzitm, ntfldnm, dcm.Decimal(val + amount, CurrencyContext))

                val = getattr(pcsmrzitm, crfldnm, None)
                if val is None:
                  val = dcm.Decimal(0, CurrencyContext)
                setattr(pcsmrzitm, crfldnm, dcm.Decimal(val + jitm.GLJITRDB, CurrencyContext))

                val = getattr(pcsmrzitm, dbfldnm, None)
                if val is None:
                  val = dcm.Decimal(0, CurrencyContext)
                setattr(pcsmrzitm, dbfldnm, dcm.Decimal(val + jitm.GLJITRCR, CurrencyContext))

                pcsmrzitm.GLSMAUDT = td.date().tointeger()
                pcsmrzitm.GLSMAUTM = td.time().tointeger()
                pcsmrzitm.GLSMAUUS = self.info_dict['usr_info'][3]

                if insmode:
                  self.session.save(pcsmrzitm)
                else:
                  self.session.update(pcsmrzitm)

          # normal posting
          if self.info_dict['job'].GLPOPOTP == 1:
            self.logger.notifyChannel('proc', ecflogger.LOG_INFO, 'updating actual summary')
            psmrzitm = GLSMRZ.get((jhdr.GLJHCONO, jitm.GLJIACID, \
              self.info_dict['glopt'].GLOPFSTP, jhdr.GLJHFSYR, \
              1, jitm.GLJICSCD, 'F'))
            self.logger.notifyChannel('proc', ecflogger.LOG_INFO, 'adjusting functional currency summary')
            insmode = False
            if not psmrzitm:
              insmode = True
              psmrzitm = GLSMRZ(
                GLSMCONO = jhdr.GLJHCONO,
                GLSMACID = jitm.GLJIACID,
                GLSMFSTP = self.info_dict['glopt'].GLOPFSTP,
                GLSMFSYR = jhdr.GLJHFSYR,
                GLSMSMTP = 1,
                GLSMCUCD = jitm.GLJICSCD,
                GLSMCUTP = 'F',
                GLSMAUDT = td.date().tointeger(),
                GLSMAUTM = td.time().tointeger(),
                GLSMAUUS = self.info_dict['usr_info'][3])
            ntfldnm = 'GLNTPR%.2d' % jhdr.GLJHFSPR
            crfldnm = 'GLCRPR%.2d' % jhdr.GLJHFSPR
            dbfldnm = 'GLDBPR%.2d' % jhdr.GLJHFSPR

            dcm.getcontext().prec = 9
            val = getattr(psmrzitm, ntfldnm, None)
            if val is None:
              val = dcm.Decimal(0, CurrencyContext)
            setattr(psmrzitm, ntfldnm, dcm.Decimal(val + jitm.GLJICUAM, CurrencyContext))

            val = getattr(psmrzitm, crfldnm, None)
            if val is None:
              val = dcm.Decimal(0, CurrencyContext)
            setattr(psmrzitm, crfldnm, dcm.Decimal(val + jitm.GLJICUCR, CurrencyContext))

            val = getattr(psmrzitm, dbfldnm, None)
            if val is None:
              val = dcm.Decimal(0, CurrencyContext)
            setattr(psmrzitm, dbfldnm, dcm.Decimal(val + jitm.GLJICUDB, CurrencyContext))

            psmrzitm.GLSMAUDT = td.date().tointeger()
            psmrzitm.GLSMAUTM = td.time().tointeger()
            psmrzitm.GLSMAUUS = self.info_dict['usr_info'][3]

            if insmode:
              self.session.save(psmrzitm)
            else:
              self.session.update(psmrzitm)

            if jitm.GLJICSCD != jitm.GLJICHCD:
              self.logger.notifyChannel('proc', ecflogger.LOG_INFO, 'adjusting source currency summary')
              pcsmrzitm = GLSMRZ.get((jhdr.GLJHCONO, jitm.GLJIACID, \
                self.info_dict['glopt'].GLOPFSTP, jhdr.GLJHFSYR, \
                1, jitm.GLJICHCD, 'S'))
              insmode = False
              if not pcsmrzitm:
                insmode = True
                pcsmrzitm = GLSMRZ(
                  GLSMCONO = jhdr.GLJHCONO,
                  GLSMACID = jitm.GLJIACID,
                  GLSMFSTP = self.info_dict['glopt'].GLOPFSTP,
                  GLSMFSYR = jhdr.GLJHFSYR,
                  GLSMSMTP = 1,
                  GLSMCUCD = jitm.GLJICHCD,
                  GLSMCUTP = 'S',
                  GLSMAUDT = td.date().tointeger(),
                  GLSMAUTM = td.time().tointeger(),
                  GLSMAUUS = self.info_dict['usr_info'][3])
              ntfldnm = 'GLNTPR%.2d' % jhdr.GLJHFSPR
              crfldnm = 'GLCRPR%.2d' % jhdr.GLJHFSPR
              dbfldnm = 'GLDBPR%.2d' % jhdr.GLJHFSPR

              dcm.getcontext().prec = 9
              val = getattr(pcsmrzitm, ntfldnm, None)
              if val is None:
                val = dcm.Decimal(0, CurrencyContext)
              setattr(pcsmrzitm, ntfldnm, dcm.Decimal(val + jitm.GLJITRAM, CurrencyContext))

              val = getattr(pcsmrzitm, crfldnm, None)
              if val is None:
                val = dcm.Decimal(0, CurrencyContext)
              setattr(pcsmrzitm, crfldnm, dcm.Decimal(val + jitm.GLJITRCR, CurrencyContext))

              val = getattr(pcsmrzitm, dbfldnm, None)
              if val is None:
                val = dcm.Decimal(0, CurrencyContext)
              setattr(pcsmrzitm, dbfldnm, dcm.Decimal(val + jitm.GLJITRDB, CurrencyContext))

              pcsmrzitm.GLSMAUDT = td.date().tointeger()
              pcsmrzitm.GLSMAUTM = td.time().tointeger()
              pcsmrzitm.GLSMAUUS = self.info_dict['usr_info'][3]

              if insmode:
                self.session.save(pcsmrzitm)
              else:
                self.session.update(pcsmrzitm)

            if (jhdr.GLJHJERV == 1):
              self.logger.notifyChannel('proc', ecflogger.LOG_INFO, 'adjusting reversal summary')
              nxtprd = CSYFSP.getNextPeriod(self.info_dict['glopt'].GLOPFSTP, \
                jhdr.GLJHFSYR, jhdr.GLJHFSPR)
              if not nxtprd:
                raise EPostingError('No appropriate fiscal period to post reversal journal')

              if nxtprd[0] != psmrzitm.GLSMFSYR:
                psmrzitm = GLSMRZ.get((jhdr.GLJHCONO, jitm.GLJIACID, \
                  self.info_dict['glopt'].GLOPFSTP, jhdr.GLJHFSYR, \
                  2, jitm.GLJICSCD, 'F'))

              insmode = False
              if not psmrzitm:
                insmode = True
                psmrzitm = GLSMRZ(
                  GLSMCONO = jhdr.GLJHCONO,
                  GLSMACID = jitm.GLJIACID,
                  GLSMFSTP = self.info_dict['glopt'].GLOPFSTP,
                  GLSMFSYR = nxtprd[0],
                  GLSMSMTP = 1,
                  GLSMCUCD = jitm.GLJICSCD,
                  GLSMCUTP = 'F',
                  GLSMAUDT = td.date().tointeger(),
                  GLSMAUTM = td.time().tointeger(),
                  GLSMAUUS = self.info_dict['usr_info'][3])

              ntfldnm = 'GLNTPR%.2d' % nxtprd[1]
              crfldnm = 'GLCRPR%.2d' % nxtprd[1]
              dbfldnm = 'GLDBPR%.2d' % nxtprd[1]

              dcm.getcontext().prec = 9
              namount = dcm.Decimal(jitm.GLJICUAM * dcm.Decimal(-1, CurrencyContext), CurrencyContext)
              val = getattr(psmrzitm, ntfldnm, None)
              if val is None:
                val = dcm.Decimal(0, CurrencyContext)
              setattr(psmrzitm, ntfldnm, dcm.Decimal(val + namount, CurrencyContext))

              val = getattr(psmrzitm, crfldnm, None)
              if val is None:
                val = dcm.Decimal(0, CurrencyContext)
              setattr(psmrzitm, crfldnm, dcm.Decimal(val + jitm.GLJICUDB, CurrencyContext))

              val = getattr(psmrzitm, dbfldnm, None)
              if val is None:
                val = dcm.Decimal(0, CurrencyContext)
              setattr(psmrzitm, dbfldnm, dcm.Decimal(val + jitm.GLJICUCR, CurrencyContext))

              psmrzitm.GLSMAUDT = td.date().tointeger()
              psmrzitm.GLSMAUTM = td.time().tointeger()
              psmrzitm.GLSMAUUS = self.info_dict['usr_info'][3]

              if insmode:
                self.session.save(psmrzitm)
              else:
                self.session.update(psmrzitm)

              if jitm.GLJICSCD != jitm.GLJICHCD:

                if nxtprd[0] != pcsmrzitm.GLSMFSYR:
                  pcsmrzitm = GLSMRZ.get((jhdr.GLJHCONO, jitm.GLJIACID, \
                  self.info_dict['glopt'].GLOPFSTP, nxtprd[0], \
                  1, jitm.GLJICHCD, 'S'))

                insmode = False
                if not pcsmrzitm:
                  insmode = True
                  pcsmrzitm = GLSMRZ(
                    GLSMCONO = jhdr.GLJHCONO,
                    GLSMACID = jitm.GLJIACID,
                    GLSMFSTP = self.info_dict['glopt'].GLOPFSTP,
                    GLSMFSYR = nxtprd[0],
                    GLSMSMTP = 1,
                    GLSMCUCD = jitm.GLJICHCD,
                    GLSMCUTP = 'S',
                    GLSMAUDT = td.date().tointeger(),
                    GLSMAUTM = td.time().tointeger(),
                    GLSMAUUS = self.info_dict['usr_info'][3])

                ntfldnm = 'GLNTPR%.2d' % nxtprd[1]
                crfldnm = 'GLCRPR%.2d' % nxtprd[1]
                dbfldnm = 'GLDBPR%.2d' % nxtprd[1]

                dcm.getcontext().prec = 9
                amount = dcm.Decimal(jitm.GLJITRAM * dcm.Decimal(-1, \
                  CurrencyContext), CurrencyContext)
                val = getattr(pcsmrzitm, ntfldnm, None)
                if val is None:
                  val = dcm.Decimal(0, CurrencyContext)
                setattr(pcsmrzitm, ntfldnm, dcm.Decimal(val + amount, \
                  CurrencyContext))

                val = getattr(pcsmrzitm, crfldnm, None)
                if val is None:
                  val = dcm.Decimal(0, CurrencyContext)
                setattr(pcsmrzitm, crfldnm, dcm.Decimal(val + jitm.GLJITRDB, \
                  CurrencyContext))

                val = getattr(pcsmrzitm, dbfldnm, None)
                if val is None:
                  val = dcm.Decimal(0, CurrencyContext)
                setattr(pcsmrzitm, dbfldnm, dcm.Decimal(val + jitm.GLJITRCR, \
                  CurrencyContext))

                pcsmrzitm.GLSMAUDT = td.date().tointeger()
                pcsmrzitm.GLSMAUTM = td.time().tointeger()
                pcsmrzitm.GLSMAUUS = self.info_dict['usr_info'][3]

                if insmode:
                  self.session.save(pcsmrzitm)
                else:
                  self.session.update(pcsmrzitm)

        # allocated account posting procedures
        elif (acctid.GLACALST == 1):
          self.logger.notifyChannel('proc', ecflogger.LOG_INFO, 'INFO: Transaction acct is allocated')
          alaccts = GLALAC.getObj(True, GLALCONO = acctid.GLACCONO, \
            GLALACID = acctid.GLACACID)
          for alacct in alaccts:
            if self.info_dict['job'].GLPOPOTP == 2:
              # provisional posting
              self.logger.notifyChannel('proc', ecflogger.LOG_INFO, 'creating provisional summary for %s' % alacct.GLALALID)
              psmrzitm = GLSMRZ.get((jhdr.GLJHCONO, alacct.GLALALID, \
                self.info_dict['glopt'].GLOPFSTP, jhdr.GLJHFSYR, \
                2, jitm.GLJICSCD, 'F'))
              insmode = False
              if not psmrzitm:
                insmode = True
                psmrzitm = GLSMRZ(
                  GLSMCONO = jhdr.GLJHCONO,
                  GLSMACID = alacct.GLALALID,
                  GLSMFSTP = self.info_dict['glopt'].GLOPFSTP,
                  GLSMFSYR = jhdr.GLJHFSYR,
                  GLSMSMTP = 2,
                  GLSMCUCD = jitm.GLJICSCD,
                  GLSMCUTP = 'F',
                  GLSMAUDT = td.date().tointeger(),
                  GLSMAUTM = td.time().tointeger(),
                  GLSMAUUS = self.info_dict['usr_info'][3])
              ntfldnm = 'GLNTPR%.2d' % jhdr.GLJHFSPR
              crfldnm = 'GLCRPR%.2d' % jhdr.GLJHFSPR
              dbfldnm = 'GLDBPR%.2d' % jhdr.GLJHFSPR

              dcm.getcontext().prec = 9
              alcuam = (dcm.Decimal(jitm.GLJICUAM) * dcm.Decimal(alacct.GLALALPC)) / dcm.Decimal(100)
              alcucr = (dcm.Decimal(jitm.GLJICUCR) * dcm.Decimal(alacct.GLALALPC)) / dcm.Decimal(100)
              alcudb = (dcm.Decimal(jitm.GLJICUDB) * dcm.Decimal(alacct.GLALALPC)) / dcm.Decimal(100)

              altram = (dcm.Decimal(jitm.GLJITRAM) * dcm.Decimal(alacct.GLALALPC)) / dcm.Decimal(100)
              altrcr = (dcm.Decimal(jitm.GLJITRCR) * dcm.Decimal(alacct.GLALALPC)) / dcm.Decimal(100)
              altrdb = (dcm.Decimal(jitm.GLJITRDB) * dcm.Decimal(alacct.GLALALPC)) / dcm.Decimal(100)

              val = getattr(psmrzitm, ntfldnm, None)
              if val is None:
                val = dcm.Decimal(0, CurrencyContext)
              setattr(psmrzitm, ntfldnm, dcm.Decimal(val + alcuam, CurrencyContext))

              val = getattr(psmrzitm, crfldnm, None)
              if val is None:
                val = dcm.Decimal(0, CurrencyContext)
              setattr(psmrzitm, crfldnm, dcm.Decimal(val + alcucr, CurrencyContext))

              val = getattr(psmrzitm, dbfldnm, None)
              if val is None:
                val = dcm.Decimal(0, CurrencyContext)
              setattr(psmrzitm, dbfldnm, dcm.Decimal(val + alcudb, CurrencyContext))

              psmrzitm.GLSMAUDT = td.date().tointeger()
              psmrzitm.GLSMAUTM = td.time().tointeger()
              psmrzitm.GLSMAUUS = self.info_dict['usr_info'][3]

              if insmode:
                self.session.save(psmrzitm)
              else:
                self.session.update(psmrzitm)

              if jitm.GLJICSCD != jitm.GLJICHCD:
                pcsmrzitm = GLSMRZ.get((jhdr.GLJHCONO, alacct.GLALALID, \
                  self.info_dict['glopt'].GLOPFSTP, jhdr.GLJHFSYR, \
                  2, jitm.GLJICHCD, 'S'))
                insmode = False
                if not pcsmrzitm:
                  insmode = True
                  pcsmrzitm = GLSMRZ(
                    GLSMCONO = jhdr.GLJHCONO,
                    GLSMACID = alacct.GLALALID,
                    GLSMFSTP = self.info_dict['glopt'].GLOPFSTP,
                    GLSMFSYR = jhdr.GLJHFSYR,
                    GLSMSMTP = 2,
                    GLSMCUCD = jitm.GLJICHCD,
                    GLSMCUTP = 'S',
                    GLSMAUDT = td.date().tointeger(),
                    GLSMAUTM = td.time().tointeger(),
                    GLSMAUUS = self.info_dict['usr_info'][3])
                ntfldnm = 'GLNTPR%.2d' % jhdr.GLJHFSPR
                crfldnm = 'GLCRPR%.2d' % jhdr.GLJHFSPR
                dbfldnm = 'GLDBPR%.2d' % jhdr.GLJHFSPR

                dcm.getcontext().prec = 9
                val = getattr(pcsmrzitm, ntfldnm, None)
                if val is None:
                  val = dcm.Decimal(0, CurrencyContext)
                setattr(pcsmrzitm, ntfldnm, dcm.Decimal(val + altram, CurrencyContext))

                val = getattr(pcsmrzitm, crfldnm, None)
                if val is None:
                  val = dcm.Decimal(0, CurrencyContext)
                setattr(pcsmrzitm, crfldnm, dcm.Decimal(val + altrcr, CurrencyContext))

                val = getattr(pcsmrzitm, dbfldnm, None)
                if val is None:
                  val = dcm.Decimal(0, CurrencyContext)
                setattr(pcsmrzitm, dbfldnm, dcm.Decimal(val + altrdb, CurrencyContext))

                pcsmrzitm.GLSMAUDT = td.date().tointeger()
                pcsmrzitm.GLSMAUTM = td.time().tointeger()
                pcsmrzitm.GLSMAUUS = self.info_dict['usr_info'][3]

                if insmode:
                  self.session.save(pcsmrzitm)
                else:
                  self.session.update(pcsmrzitm)

              if (jhdr.GLJHJERV == 1):
                nxtprd = CSYFSP.getNextPeriod(self.info_dict['glopt'].GLOPFSTP, \
                  jhdr.GLJHFSYR, jhdr.GLJHFSPR)
                if not nxtprd:
                  raise EPostingError('No appropriate fiscal period to post reversal journal')

                if nxtprd[0] != psmrzitm.GLSMFSYR:
                  psmrzitm = GLSMRZ.get((jhdr.GLJHCONO, alacct.GLALALID, \
                    self.info_dict['glopt'].GLOPFSTP, jhdr.GLJHFSYR, \
                    2, jitm.GLJICSCD, 'F'))

                insmode = False
                if not psmrzitm:
                  insmode = True
                  psmrzitm = GLSMRZ(
                    GLSMCONO = jhdr.GLJHCONO,
                    GLSMACID = alacct.GLALALID,
                    GLSMFSTP = self.info_dict['glopt'].GLOPFSTP,
                    GLSMFSYR = nxtprd[0],
                    GLSMSMTP = 2,
                    GLSMCUCD = jitm.GLJICSCD,
                    GLSMCUTP = 'F',
                    GLSMAUDT = td.date().tointeger(),
                    GLSMAUTM = td.time().tointeger(),
                    GLSMAUUS = self.info_dict['usr_info'][3])

                ntfldnm = 'GLNTPR%.2d' % nxtprd[1]
                crfldnm = 'GLCRPR%.2d' % nxtprd[1]
                dbfldnm = 'GLDBPR%.2d' % nxtprd[1]

                dcm.getcontext().prec = 9
                namount = dcm.Decimal(alcuam * dcm.Decimal(-1, CurrencyContext), CurrencyContext)
                val = getattr(psmrzitm, ntfldnm, None)
                if val is None:
                  val = dcm.Decimal(0, CurrencyContext)
                setattr(psmrzitm, ntfldnm, dcm.Decimal(val + namount, CurrencyContext))

                val = getattr(psmrzitm, crfldnm, None)
                if val is None:
                  val = dcm.Decimal(0, CurrencyContext)
                setattr(psmrzitm, crfldnm, dcm.Decimal(val + alcudb, CurrencyContext))

                val = getattr(psmrzitm, dbfldnm, None)
                if val is None:
                  val = dcm.Decimal(0, CurrencyContext)
                setattr(psmrzitm, dbfldnm, dcm.Decimal(val + alcucr, CurrencyContext))

                psmrzitm.GLSMAUDT = td.date().tointeger()
                psmrzitm.GLSMAUTM = td.time().tointeger()
                psmrzitm.GLSMAUUS = self.info_dict['usr_info'][3]

                if insmode:
                  self.session.save(psmrzitm)
                else:
                  self.session.update(psmrzitm)

                if jitm.GLJICSCD != jitm.GLJICHCD:

                  if nxtprd[0] != pcsmrzitm.GLSMFSYR:
                    pcsmrzitm = GLSMRZ.get((jhdr.GLJHCONO, alacct.GLALALID, \
                      self.info_dict['glopt'].GLOPFSTP, nxtprd[0], \
                      2, jitm.GLJICHCD, 'S'))

                  insmode = False
                  if not pcsmrzitm:
                    insmode = True
                    pcsmrzitm = GLSMRZ(
                      GLSMCONO = jhdr.GLJHCONO,
                      GLSMACID = alacct.GLALALID,
                      GLSMFSTP = self.info_dict['glopt'].GLOPFSTP,
                      GLSMFSYR = nxtprd[0],
                      GLSMSMTP = 2,
                      GLSMCUCD = jitm.GLJICHCD,
                      GLSMCUTP = 'S',
                      GLSMAUDT = td.date().tointeger(),
                      GLSMAUTM = td.time().tointeger(),
                      GLSMAUUS = self.info_dict['usr_info'][3])

                  ntfldnm = 'GLNTPR%.2d' % nxtprd[1]
                  crfldnm = 'GLCRPR%.2d' % nxtprd[1]
                  dbfldnm = 'GLDBPR%.2d' % nxtprd[1]

                  dcm.getcontext().prec = 9
                  amount = dcm.Decimal(altram * dcm.Decimal(-1, CurrencyContext), CurrencyContext)
                  val = getattr(pcsmrzitm, ntfldnm, None)
                  if val is None:
                    val = dcm.Decimal(0, CurrencyContext)
                  setattr(pcsmrzitm, ntfldnm, dcm.Decimal(val + amount, CurrencyContext))

                  val = getattr(pcsmrzitm, crfldnm, None)
                  if val is None:
                    val = dcm.Decimal(0, CurrencyContext)
                  setattr(pcsmrzitm, crfldnm, dcm.Decimal(val + altrdb, CurrencyContext))

                  val = getattr(pcsmrzitm, dbfldnm, None)
                  if val is None:
                    val = dcm.Decimal(0, CurrencyContext)
                  setattr(pcsmrzitm, dbfldnm, dcm.Decimal(val + altrcr, CurrencyContext))

                  pcsmrzitm.GLSMAUDT = td.date().tointeger()
                  pcsmrzitm.GLSMAUTM = td.time().tointeger()
                  pcsmrzitm.GLSMAUUS = self.info_dict['usr_info'][3]

                  if insmode:
                    self.session.save(pcsmrzitm)
                  else:
                    self.session.update(pcsmrzitm)

            # normal posting
            if self.info_dict['job'].GLPOPOTP == 1:
              self.logger.notifyChannel('proc', ecflogger.LOG_INFO, 'adjusting actual summary for %s' % alacct.GLALALID)
              psmrzitm = GLSMRZ.get((jhdr.GLJHCONO, alacct.GLALALID, \
                self.info_dict['glopt'].GLOPFSTP, jhdr.GLJHFSYR, \
                1, jitm.GLJICSCD, 'F'))
              insmode = False
              if not psmrzitm:
                insmode = True
                psmrzitm = GLSMRZ(
                  GLSMCONO = jhdr.GLJHCONO,
                  GLSMACID = alacct.GLALALID,
                  GLSMFSTP = self.info_dict['glopt'].GLOPFSTP,
                  GLSMFSYR = jhdr.GLJHFSYR,
                  GLSMSMTP = 1,
                  GLSMCUCD = jitm.GLJICSCD,
                  GLSMCUTP = 'F',
                  GLSMAUDT = td.date().tointeger(),
                  GLSMAUTM = td.time().tointeger(),
                  GLSMAUUS = self.info_dict['usr_info'][3])
              ntfldnm = 'GLNTPR%.2d' % jhdr.GLJHFSPR
              crfldnm = 'GLCRPR%.2d' % jhdr.GLJHFSPR
              dbfldnm = 'GLDBPR%.2d' % jhdr.GLJHFSPR

              dcm.getcontext().prec = 9
              alcuam = (dcm.Decimal(jitm.GLJICUAM) * dcm.Decimal(alacct.GLALALPC)) / dcm.Decimal(100)
              alcucr = (dcm.Decimal(jitm.GLJICUCR) * dcm.Decimal(alacct.GLALALPC)) / dcm.Decimal(100)
              alcudb = (dcm.Decimal(jitm.GLJICUDB) * dcm.Decimal(alacct.GLALALPC)) / dcm.Decimal(100)

              altram = (dcm.Decimal(jitm.GLJITRAM) * dcm.Decimal(alacct.GLALALPC)) / dcm.Decimal(100)
              altrcr = (dcm.Decimal(jitm.GLJITRCR) * dcm.Decimal(alacct.GLALALPC)) / dcm.Decimal(100)
              altrdb = (dcm.Decimal(jitm.GLJITRDB) * dcm.Decimal(alacct.GLALALPC)) / dcm.Decimal(100)

              val = getattr(psmrzitm, ntfldnm, None)
              if val is None:
                val = dcm.Decimal(0, CurrencyContext)
              setattr(psmrzitm, ntfldnm, dcm.Decimal(val + alcuam, CurrencyContext))

              val = getattr(psmrzitm, crfldnm, None)
              if val is None:
                val = dcm.Decimal(0, CurrencyContext)
              setattr(psmrzitm, crfldnm, dcm.Decimal(val + alcucr, CurrencyContext))

              val = getattr(psmrzitm, dbfldnm, None)
              if val is None:
                val = dcm.Decimal(0, CurrencyContext)
              setattr(psmrzitm, dbfldnm, dcm.Decimal(val + alcudb, CurrencyContext))

              psmrzitm.GLSMAUDT = td.date().tointeger()
              psmrzitm.GLSMAUTM = td.time().tointeger()
              psmrzitm.GLSMAUUS = self.info_dict['usr_info'][3]

              if insmode:
                self.session.save(psmrzitm)
              else:
                self.session.update(psmrzitm)

              if jitm.GLJICSCD != jitm.GLJICHCD:
                pcsmrzitm = GLSMRZ.get((jhdr.GLJHCONO, alacct.GLALALID, \
                  self.info_dict['glopt'].GLOPFSTP, jhdr.GLJHFSYR, \
                  1, jitm.GLJICHCD, 'S'))
                insmode = False
                if not pcsmrzitm:
                  insmode = True
                  pcsmrzitm = GLSMRZ(
                    GLSMCONO = jhdr.GLJHCONO,
                    GLSMACID = alacct.GLALALID,
                    GLSMFSTP = self.info_dict['glopt'].GLOPFSTP,
                    GLSMFSYR = jhdr.GLJHFSYR,
                    GLSMSMTP = 1,
                    GLSMCUCD = jitm.GLJICHCD,
                    GLSMCUTP = 'S',
                    GLSMAUDT = td.date().tointeger(),
                    GLSMAUTM = td.time().tointeger(),
                    GLSMAUUS = self.info_dict['usr_info'][3])
                ntfldnm = 'GLNTPR%.2d' % jhdr.GLJHFSPR
                crfldnm = 'GLCRPR%.2d' % jhdr.GLJHFSPR
                dbfldnm = 'GLDBPR%.2d' % jhdr.GLJHFSPR

                dcm.getcontext().prec = 9
                val = getattr(pcsmrzitm, ntfldnm, None)
                if val is None:
                  val = dcm.Decimal(0, CurrencyContext)
                setattr(pcsmrzitm, ntfldnm, dcm.Decimal(val + altram, CurrencyContext))

                val = getattr(pcsmrzitm, crfldnm, None)
                if val is None:
                  val = dcm.Decimal(0, CurrencyContext)
                setattr(pcsmrzitm, crfldnm, dcm.Decimal(val + altrcr, CurrencyContext))

                val = getattr(pcsmrzitm, dbfldnm, None)
                if val is None:
                  val = dcm.Decimal(0, CurrencyContext)
                setattr(pcsmrzitm, dbfldnm, dcm.Decimal(val + altrdb, CurrencyContext))

                pcsmrzitm.GLSMAUDT = td.date().tointeger()
                pcsmrzitm.GLSMAUTM = td.time().tointeger()
                pcsmrzitm.GLSMAUUS = self.info_dict['usr_info'][3]

                if insmode:
                  self.session.save(pcsmrzitm)
                else:
                  self.session.update(pcsmrzitm)

              if (jhdr.GLJHJERV == 1):
                nxtprd = CSYFSP.getNextPeriod(self.info_dict['glopt'].GLOPFSTP, \
                  jhdr.GLJHFSYR, jhdr.GLJHFSPR)
                if not nxtprd:
                  raise EPostingError('No appropriate fiscal period to post reversal journal')

                if nxtprd[0] != psmrzitm.GLSMFSYR:
                  psmrzitm = GLSMRZ.get((jhdr.GLJHCONO, alacct.GLALALID, \
                    self.info_dict['glopt'].GLOPFSTP, jhdr.GLJHFSYR, \
                    2, jitm.GLJICSCD, 'F'))

                insmode = False
                if not psmrzitm:
                  insmode = True
                  psmrzitm = GLSMRZ(
                    GLSMCONO = jhdr.GLJHCONO,
                    GLSMACID = alacct.GLALALID,
                    GLSMFSTP = self.info_dict['glopt'].GLOPFSTP,
                    GLSMFSYR = nxtprd[0],
                    GLSMSMTP = 1,
                    GLSMCUCD = jitm.GLJICSCD,
                    GLSMCUTP = 'F',
                    GLSMAUDT = td.date().tointeger(),
                    GLSMAUTM = td.time().tointeger(),
                    GLSMAUUS = self.info_dict['usr_info'][3])

                ntfldnm = 'GLNTPR%.2d' % nxtprd[1]
                crfldnm = 'GLCRPR%.2d' % nxtprd[1]
                dbfldnm = 'GLDBPR%.2d' % nxtprd[1]

                dcm.getcontext().prec = 9
                namount = dcm.Decimal(alcuam * dcm.Decimal(-1, CurrencyContext), CurrencyContext)
                val = getattr(psmrzitm, ntfldnm, None)
                if val is None:
                  val = dcm.Decimal(0, CurrencyContext)
                setattr(psmrzitm, ntfldnm, dcm.Decimal(val + namount, CurrencyContext))

                val = getattr(psmrzitm, crfldnm, None)
                if val is None:
                  val = dcm.Decimal(0, CurrencyContext)
                setattr(psmrzitm, crfldnm, dcm.Decimal(val + alcudb, CurrencyContext))

                val = getattr(psmrzitm, dbfldnm, None)
                if val is None:
                  val = dcm.Decimal(0, CurrencyContext)
                setattr(psmrzitm, dbfldnm, dcm.Decimal(val + alcucr, CurrencyContext))

                psmrzitm.GLSMAUDT = td.date().tointeger()
                psmrzitm.GLSMAUTM = td.time().tointeger()
                psmrzitm.GLSMAUUS = self.info_dict['usr_info'][3]

                if insmode:
                  self.session.save(psmrzitm)
                else:
                  self.session.update(psmrzitm)

                if jitm.GLJICSCD != jitm.GLJICHCD:

                  if nxtprd[0] != pcsmrzitm.GLSMFSYR:
                    pcsmrzitm = GLSMRZ.get((jhdr.GLJHCONO, alacct.GLALALID, \
                    self.info_dict['glopt'].GLOPFSTP, nxtprd[0], \
                    1, jitm.GLJICHCD, 'S'))

                  insmode = False
                  if not pcsmrzitm:
                    insmode = True
                    pcsmrzitm = GLSMRZ(
                      GLSMCONO = jhdr.GLJHCONO,
                      GLSMACID = alacct.GLALALID,
                      GLSMFSTP = self.info_dict['glopt'].GLOPFSTP,
                      GLSMFSYR = nxtprd[0],
                      GLSMSMTP = 1,
                      GLSMCUCD = jitm.GLJICHCD,
                      GLSMCUTP = 'S',
                      GLSMAUDT = td.date().tointeger(),
                      GLSMAUTM = td.time().tointeger(),
                      GLSMAUUS = self.info_dict['usr_info'][3])

                  ntfldnm = 'GLNTPR%.2d' % nxtprd[1]
                  crfldnm = 'GLCRPR%.2d' % nxtprd[1]
                  dbfldnm = 'GLDBPR%.2d' % nxtprd[1]

                  dcm.getcontext().prec = 9
                  amount = dcm.Decimal(altram * dcm.Decimal(-1, CurrencyContext), CurrencyContext)
                  val = getattr(pcsmrzitm, ntfldnm, None)
                  if val is None:
                    val = dcm.Decimal(0, CurrencyContext)
                  setattr(pcsmrzitm, ntfldnm, dcm.Decimal(val + amount, CurrencyContext))

                  val = getattr(pcsmrzitm, crfldnm, None)
                  if val is None:
                    val = dcm.Decimal(0, CurrencyContext)
                  setattr(pcsmrzitm, crfldnm, dcm.Decimal(val + altrdb, CurrencyContext))

                  val = getattr(pcsmrzitm, dbfldnm, None)
                  if val is None:
                    val = dcm.Decimal(0, CurrencyContext)
                  setattr(pcsmrzitm, dbfldnm, dcm.Decimal(val + altrcr, CurrencyContext))

                  pcsmrzitm.GLSMAUDT = td.date().tointeger()
                  pcsmrzitm.GLSMAUTM = td.time().tointeger()
                  pcsmrzitm.GLSMAUUS = self.info_dict['usr_info'][3]

                  if insmode:
                    self.session.save(pcsmrzitm)
                  else:
                    self.session.update(pcsmrzitm)
        self.logger.notifyChannel('proc', ecflogger.LOG_INFO, 'END:posting transaction')
      self.session.commit()
    except EPostingError:
      self.session.rollback()
      raise
    except Exception:
      self.session.rollback()
      raise


  def do_postBatch(self, bctl):
    self.logger.notifyChannel('proc', ecflogger.LOG_INFO, 'Posting batch %s-%.6d' % (bctl.GLBCNOID, bctl.GLBCLSID))
    q = GLJHDR.query
    q = q.filter_by(GLJHCONO = bctl.GLBCCONO)
    q = q.filter_by(GLJHNOID = bctl.GLBCNOID)
    q = q.filter_by(GLJHBCID = bctl.GLBCLSID)
    q = q.order_by(sa.asc(GLJHDR.GLJHCONO))
    q = q.order_by(sa.asc(GLJHDR.GLJHNOID))
    q = q.order_by(sa.asc(GLJHDR.GLJHBCID))
    q = q.order_by(sa.asc(GLJHDR.GLJHJEID))
    jhdrs = q.all()

    error_jhdr = list()
    success_cnt = 0

    for jhdr in jhdrs:
      self.logger.notifyChannel('proc', ecflogger.LOG_INFO, 'Validating journal %.6d' % (jhdr.GLJHJEID))
      if self.info_dict['job'].GLPOPOTP == 2:
        # prepare provisional summary for current fiscal period
        self.prepProvSumrz(jhdr, jhdr.GLJHFSYR)
        if jhdr.GLJHJERV == 1:
          # prepare provisional summary for reversal fiscal period
          nxtprd = CSYFSP.getNextPeriod(self.info_dict['glopt'].GLOPFSTP, \
                    jhdr.GLJHFSYR, jhdr.GLJHFSPR)
          if not nxtprd:
            raise EPostingError('No appropriate fiscal period to post reversal journal')
          self.prepProvSumrz(jhdr, nxtprd[0])
      try:
        self.do_postJV(bctl, jhdr)
        success_cnt += 1
      except:
        if self.info_dict['job'].GLPOPOTP == 1:
          self.session.clear()
          error_jhdr.append(jhdr)
        else:
          raise

    if len(error_jhdr) > 0:
      if (success_cnt == 0) and (self.info_dict['err_batch'] == None):
        bctl.GLBCNODS  = 'Error Batch'
        bctl.GLBCBCST  = 5
        if not self.session.transaction_started():
          self.session.begin()
        try:
          self.session.update(bctl)
          self.session.commit()
          self.info_dict['err_batch'] = bctl
        except:
          self.session.rollback()
          self.session.clear()
      for hdr in error_jhdr:
        self.do_moveErrorJV(bctl, hdr)

    if (success_cnt > 0) and (self.info_dict['err_batch'] != bctl) and \
       (self.info_dict['job'].GLPOPOTP == 1):
      bctl.GLBCBCST  = 3
      if not self.session.transaction_started():
        self.session.begin()
      try:
        self.session.update(bctl)
        self.session.commit()
      except:
        self.session.rollback()
        self.session.clear()

  def executeJob(self, jobsession):
    job = GLPOST.get(jobsession.jobID)
    if not job:
      raise Exception('Job information could not be found')

    self.logger.notifyChannel('init', ecflogger.LOG_INFO, 'Retrieving system information')

    proxy = self.getBusinessObjectProxy()
    usrobj = proxy.getObject('USROBJ')
    glsobj = proxy.getObject('GLSOBJ')
    info = usrobj.getUserInfoEx(job.GLPOAUUS)
    cono = info[2]

    mstcmp = MSTCMP.get(cono)
    glopt  = GLSOPT.get(cono)

    self.logger.notifyChannel('init', ecflogger.LOG_INFO, 'Retrieving batch list')
    q = GLBCTL.query
    q = q.filter_by(GLBCCONO = cono)
    q = q.filter_by(GLBCNOID = glopt.GLOPBCNO)
    if job.GLPOPOMO == 2:
      if job.GLPOBCFR:
        q = q.filter( GLBCTL.GLBCLSID >= job.GLPOBCFR)
      if job.GLPOBCTO:
        q = q.filter( GLBCTL.GLBCLSID <= job.GLPOBCTO)
    q = q.filter(sql.or_(GLBCTL.GLBCBCST == 2, GLBCTL.GLBCBCST == 5))
    q = q.order_by(sa.asc(GLBCTL.GLBCCONO))
    q = q.order_by(sa.asc(GLBCTL.GLBCNOID))
    q = q.order_by(sa.asc(GLBCTL.GLBCLSID))
    bctls = q.all()

    self.logger.notifyChannel('init', ecflogger.LOG_INFO, 'Mapping reference info')
    self.info_dict['jobsession'] = jobsession
    self.info_dict['job'] = job
    self.info_dict['usr_info'] = info
    self.info_dict['cmp'] = mstcmp
    self.info_dict['glopt'] = glopt
    self.info_dict['err_batch'] = None
    self.session = session

    for bctl in bctls:
      self.do_postBatch(bctl)












