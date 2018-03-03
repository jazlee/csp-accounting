"""
JGLS240 JOB Module purposed to create Batch Entry journal(s) for currency
exchange revaluation.
"""

__author__    = 'Jaimy Azle'
__version__   = '1.0'
__copyright__ = 'Copyright (c) 2008 Jaimy Azle'

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
from tbl import GLACCT, EFUSRS, GLSOPT, MSTCMP, GLHIST, GLBCRV, GLRVAL, GLSCST
from tbl import GLBCNO, GLBCTL, GLJHDR, GLJITM, GLSCSI, CSYFSP, MSTCRT

class JGLS240(JOBEngine):
  """
  JGLS240 JOB Module purposed to create Batch Entry journal(s) for currency
  exchange revaluation.
  """

  def __init__(self, pool):
    """
    Initializing this object, prepare global variable used for calculation
    process
    """
    super(JGLS240, self).__init__(pool)
    self.session = None
    self.info_dict = {}
    self.logger = ecflogger.Logger()
    self.reval_acct = {}
    self.revalref = None
    self.batch = None

  def do_prepareBatch(self):
    """
    Prepare the batch
    """
    self.logger.notifyChannel('proc', ecflogger.LOG_INFO, 'Preparing journal batch')
    glopt = self.info_dict['glopt']
    job = self.info_dict['job']
    self.revalref = GLRVAL.get((job.GLRVCONO, job.GLRVRVNM))
    if not self.revalref:
      raise Exception('Revaluation code does not found')

    td = dt.datetime.now()
    if job.GLRVCRBC == 1:
      lsno = GLBCNO.getLSNO(glopt.GLOPBCNO)
      self.batch = GLBCTL()
      self.batch.GLBCCONO  = self.info_dict['cono']
      self.batch.GLBCNOID  = glopt.GLOPBCNO
      self.batch.GLBCLSID  = lsno
      self.batch.GLBCNODS  = 'Revaluation Batch'
      self.batch.GLBCLSTR  = 1
      self.batch.GLBCCTTR  = 0
      self.batch.GLBCCTER  = 0
      self.batch.GLBCNTDB  = 0
      self.batch.GLBCNTCR  = 0
      self.batch.GLBCPRST  = 0
      self.batch.GLBCDTCR  = td.date().tointeger()
      self.batch.GLBCDTED  = td.date().tointeger()
      self.batch.GLBCSRLG  = 'GL'
      self.batch.GLBCBCTP  = 1
      self.batch.GLBCBCST  = 1
      self.batch.GLBCPSSQ  = 0
      self.batch.GLBCAUDT  = td.date().tointeger()
      self.batch.GLBCAUTM  = td.time().tointeger()
      self.batch.GLBCAUUS  = self.info_dict['usr_info'][3]
    else:
      self.batch = GLBCTL.get((self.info_dict['cono'], glopt.GLOPBCNO, job.GLRVBCID))
      if not self.batch:
        raise Exception('Batch could not be found')
      if self.batch.GLBCBCST != 1:
        raise Exception('selected batch status is not in OPEN mode')

  def get_JHDRID(self):
    ret = self.batch.GLBCLSTR + 1
    self.batch.GLBCLSTR = ret
    return ret

  def do_prepareJHDR(self):
    """
    Prepare journal header
    """
    self.logger.notifyChannel('proc', ecflogger.LOG_INFO, 'creating journal header')
    glopt = self.info_dict['glopt']
    job = self.info_dict['job']

    td = dt.datetime.now()
    prd = CSYFSP.findPeriod(glopt.GLOPFSTP, job.GLRVJEDT)
    if not prd:
      raise Exception('Fiscal period period for journal date %s could not be found' % job.GLRVJEDT)

    jhdr = GLJHDR()
    jhdr.GLJHCONO = self.info_dict['cono']
    jhdr.GLJHNOID = glopt.GLOPBCNO
    jhdr.GLJHBCID = self.batch.GLBCLSID
    jhdr.GLJHJEID = self.get_JHDRID()
    jhdr.GLJHBCDS = self.batch.GLBCNODS
    jhdr.GLJHFSYR = prd.SYFPFSYR
    jhdr.GLJHFSPR = prd.SYFPPRID
    jhdr.GLJHJEDS = 'Journal Entry'
    jhdr.GLJHJEDT = job.GLRVJEDT
    jhdr.GLJHJERV = 1
    jhdr.GLJHDTCR = td.date().tointeger()
    jhdr.GLJHDTED = td.date().tointeger()
    jhdr.GLJHSRLG = self.revalref.GLRVSRLG
    jhdr.GLJHSRTP = self.revalref.GLRVSRTP
    jhdr.GLJHJEST = 2 # Non-Editable
    jhdr.GLJHJEED = 1
    jhdr.GLJHLSTR = 2
    jhdr.GLJHNTDB = 0
    jhdr.GLJHNTCR = 0
    jhdr.GLJHAUDT = td.date().tointeger()
    jhdr.GLJHAUTM = td.time().tointeger()
    jhdr.GLJHAUUS = self.info_dict['usr_info'][3]
    return jhdr

  def do_createItems(self):
    """
    Create journal items
    """
    td = dt.datetime.now()
    job = self.info_dict['job']
    glopt = self.info_dict['glopt']
    for name, smrz in self.reval_acct.iteritems():
      self.logger.notifyChannel('proc', ecflogger.LOG_INFO, 'creating journal item for acct %s-%s' % (smrz[0].GLACACFM, smrz[0].GLACACNM))
      dcm.getcontext().prec = 9
      acct = smrz[0]
      amount = smrz[1]
      amountcr = dcm.Decimal(amount * dcm.Decimal(-1, CurrencyContext), CurrencyContext)
      zeroval = dcm.Decimal(0)
      if amount != zeroval:
        jhdr = self.do_prepareJHDR() # create and add journal header info
        crextp = MSTCRT.get((self.info_dict['cmp'].CMCPCUCD, self.revalref.GLRVRTTP))
        dbside = GLJITM()
        crside = GLJITM()
        # assign general info
        dbside.GLJICONO = self.info_dict['cono']
        crside.GLJICONO = self.info_dict['cono']
        dbside.GLJINOID = glopt.GLOPBCNO
        crside.GLJINOID = glopt.GLOPBCNO
        dbside.GLJIBCID = jhdr.GLJHBCID
        crside.GLJIBCID = jhdr.GLJHBCID
        dbside.GLJIJEID = jhdr.GLJHJEID
        crside.GLJIJEID = jhdr.GLJHJEID
        dbside.GLJITRID = 1
        crside.GLJITRID = 2
        dbside.GLJITRDT = td.date().tointeger()
        crside.GLJITRDT = td.date().tointeger()
        dbside.GLJISRLG = self.revalref.GLRVSRLG
        crside.GLJISRLG = self.revalref.GLRVSRLG
        dbside.GLJISRTP = self.revalref.GLRVSRTP
        crside.GLJISRTP = self.revalref.GLRVSRTP
        dbside.GLJISQNO = 1
        crside.GLJISQNO = 2
        dbside.GLJITRAM = 0
        crside.GLJITRAM = 0
        dbside.GLJITRDB = 0
        crside.GLJITRDB = 0
        dbside.GLJITRCR = 0
        crside.GLJITRCR = 0
        dbside.GLJITRTP = 1
        crside.GLJITRTP = 2
        dbside.GLJICUDC = 0
        crside.GLJICUDC = 0
        dbside.GLJICHCD = job.GLRVCUCD
        crside.GLJICHCD = job.GLRVCUCD
        dbside.GLJICSCD = self.info_dict['cmp'].CMCPCUCD
        crside.GLJICSCD = self.info_dict['cmp'].CMCPCUCD
        dbside.GLJICRTP = self.revalref.GLRVRTTP
        crside.GLJICRTP = self.revalref.GLRVRTTP
        dbside.GLJIRTDT = job.GLRVRTDT
        crside.GLJIRTDT = job.GLRVRTDT
        dbside.GLJIRCVL = job.GLRVRTVL
        crside.GLJIRCVL = job.GLRVRTVL
        dbside.GLJIRTVL = job.GLRVRTVL
        crside.GLJIRTVL = job.GLRVRTVL
        dbside.GLJIRTSP = 0
        crside.GLJIRTSP = 0
        dbside.GLJIRTOP = crextp.CMCTRTOP
        crside.GLJIRTOP = crextp.CMCTRTOP
        dbside.GLJIDTMT = crextp.CMCTDTMT
        crside.GLJIDTMT = crextp.CMCTDTMT
        dbside.GLJIAUDT = td.date().tointeger()
        crside.GLJIAUDT = td.date().tointeger()
        dbside.GLJIAUTM = td.time().tointeger()
        crside.GLJIAUTM = td.time().tointeger()
        dbside.GLJIAUUS = self.info_dict['usr_info'][3]
        crside.GLJIAUUS = self.info_dict['usr_info'][3]
        if amount < zeroval:
          dbside.GLJIACID = self.revalref.GLRVLCID
          dbside.GLJIACFM = self.revalref.GLRVLCFM
          dbside.GLJIACNM = self.revalref.GLRVLCNM
          dbside.GLJICUAM = amountcr
          dbside.GLJICUDB = amountcr
          dbside.GLJICUCR = 0
          crside.GLJIACID = acct.GLACACID
          crside.GLJIACFM = acct.GLACACFM
          crside.GLJIACNM = acct.GLACACNM
          crside.GLJICUAM = amount
          crside.GLJICUDB = 0
          crside.GLJICUCR = amountcr
        else:
          dbside.GLJIACID = acct.GLACACID
          dbside.GLJIACFM = acct.GLACACFM
          dbside.GLJIACNM = acct.GLACACNM
          dbside.GLJICUAM = amount
          dbside.GLJICUDB = amount
          dbside.GLJICUCR = 0
          crside.GLJIACID = self.revalref.GLRVGCID
          crside.GLJIACFM = self.revalref.GLRVGCFM
          crside.GLJIACNM = self.revalref.GLRVGCNM
          crside.GLJICUAM = amountcr
          crside.GLJICUDB = 0
          crside.GLJICUCR = amount
        self.session.save(jhdr)
        self.session.save(dbside)
        self.session.save(crside)

    if job.GLRVCRBC == 1:
      self.session.save(self.batch)
    else:
      self.session.update(self.batch)

  def do_calcTransaction(self, job, acct):
    """
    Calculate transaction
    """
    dcm.getcontext().prec = 9
    q = GLHIST.query
    q = q.filter_by(GLHICONO = job.GLRVCONO)
    q = q.filter_by(GLHIFSTP = job.GLRVFSTP)
    q = q.filter_by(GLHIFSYR = job.GLRVFSYR)
    q = q.filter(
          sql.and_(
            GLHIST.GLHIFSPR >= job.GLRVFPFR,
            GLHIST.GLHIFSPR <= job.GLRVFPTO
          )
        )
    q = q.filter_by(GLHIACID = acct.GLACACID)
    q = q.filter_by(GLHICHCD = job.GLRVCUCD)
    q = q.order_by(sa.asc(GLHIST.GLHICONO))
    q = q.order_by(sa.asc(GLHIST.GLHIFSTP))
    q = q.order_by(sa.asc(GLHIST.GLHIFSYR))
    q = q.order_by(sa.asc(GLHIST.GLHIIDNO))
    glhists = q.all()
    curamt = dcm.Decimal(0, CurrencyContext)
    for glhist in glhists:
      if glhist.GLHICUAM:
        self.logger.notifyChannel('proc', ecflogger.LOG_INFO, 'calculating currency exchange for acct %s-%s' % (acct.GLACACFM, acct.GLACACNM))
        dcm.getcontext().prec = 9
        amount = dcm.Decimal(glhist.GLHITRAM, CurrencyContext)
        namount = dcm.Decimal(0, CurrencyContext)
        if glhist.GLHICSCD == glhist.GLHICHCD:
          namount = amount
        else:
          if glhist.GLHIRTVL:
            if glhist.GLHIRTOP == '*':
              namount = amount * dcm.Decimal(job.GLRVRTVL)
            elif glhist.GLHIRTOP == '/':
              divider = dcm.Decimal(job.GLRVRTVL)
              if divider <> dcm.Decimal(0):
                namount = amount / divider
        if glhist.GLHICUAM != namount:
          deviation = dcm.Decimal(glhist.GLHICUAM - namount, CurrencyContext)
          curamt = dcm.Decimal(curamt + deviation, CurrencyContext)
    if curamt != dcm.Decimal(0):
      self.reval_acct[acct.GLACACID] = \
        [
          acct,
          curamt
        ]

  def do_calcReval(self):
    """
    Main entry process in creating revaluation batch entry journals
    """
    self.logger.notifyChannel('proc', ecflogger.LOG_INFO, 'Inspecting transaction')
    job = self.info_dict['job']
    q = GLACCT.query.filter_by(GLACACST = 1)
    q = q.filter_by(GLACCONO = self.info_dict['cono'])
    if job.GLRVACTP == 0:
      if job.GLRVACAL == 0:
        q = q.filter_by(
              sql.and_(
                GLACCT.GLACACID >= GLACCT.stripedacct(job.GLRVACFR),
                GLACCT.GLACACID <= GLACCT.stripedacct(job.GLRVACTO)
              )
            )
    else:
      if job.GLRVACTP > 10:
        raise Exception("Acct type is greater than maximum allowed")
      fieldName = 'GLACCS%.2d' % job.GLRVACTP
      if job.GLRVACAL == 0:
        q = q.filter(
              sql.and_(
                getattr(GLACCT, fieldName) >= GLACCT.stripedacct(job.GLRVACFR),
                getattr(GLACCT, fieldName) <= GLACCT.stripedacct(job.GLRVACTO)
              )
            )
      else:
        q = q.filter(
                sql.not_(
                  getattr(GLACCT, fieldName) == null
                )
            )
    q = q.order_by(sa.asc(GLACCT.GLACCONO))
    q = q.order_by(sa.asc(GLACCT.GLACACID))
    accts = q.all()
    for acct in accts:
      self.do_calcTransaction(job, acct)


  def executeJob(self, jobsession):
    job = GLBCRV.get(jobsession.jobID)
    if not job:
      raise Exception('Job information could not be found')

    proxy = self.getBusinessObjectProxy()
    usrobj = proxy.getObject('USROBJ')
    glsobj = proxy.getObject('GLSOBJ')
    info = usrobj.getUserInfoEx(job.GLRVAUUS)
    cono = job.GLRVCONO

    mstcmp = MSTCMP.get(cono)
    glopt  = GLSOPT.get(cono)

    self.info_dict['cono'] = cono
    self.info_dict['usr_info'] = info
    self.info_dict['cmp'] = mstcmp
    self.info_dict['glopt'] = glopt
    self.info_dict['jobsession'] = jobsession
    self.info_dict['job'] = job
    self.session = session

    self.do_calcReval()
    if len(self.reval_acct) > 0:
      self.do_prepareBatch()
      if not self.session.transaction_started():
        self.session.begin()
      try:
        self.do_createItems()
        self.session.commit()
      except:
        self.session.rollback()
        self.session.clear()
        raise




