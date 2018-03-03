from elixir import *
from jobsvc import *
import datetime as dt
from tbl import SYSCLJ, SYSCAL

class JCMN405(JOBEngine):

  def executeJob(self, jobsession):
    q = SYSCLJ.query.filter_by(SYCLJBID = jobsession.jobID)
    obj = q.first()
    if not obj:
      raise Exception('Could not find job id')

    datestart  = dt.date(obj.SYCLCLYR, 01, 01)
    datefinish = dt.date(obj.SYCLCLYR, 12, 31)
    while datestart <= datefinish:
      query = SYSCAL.query
      query = query.filter_by(SYCLCONO = obj.SYCLCONO)
      dobj  = query.filter_by(SYCLCLDT = datestart.tointeger()).first()
      td = dt.datetime.now()
      if not dobj:
        rec = SYSCAL(
            SYCLCONO = obj.SYCLCONO,
            SYCLCLDT = datestart.tointeger(),
            SYCLCLYR = datestart.year,
            SYCLCLMT = datestart.month,
            SYCLCLDW = datestart.weekday(),
            SYCLCLWD = getattr(obj, '%s%d' % ('SYCLCWD', datestart.weekday()), 1),
            SYCLCLBD = getattr(obj, '%s%d' % ('SYCLCBD', datestart.weekday()), 1),
            SYCLCLPD = getattr(obj, '%s%d' % ('SYCLCPD', datestart.weekday()), 1),
            SYCLAUDT = td.date().tointeger(),
            SYCLAUTM = td.time().tointeger(),
            SYCLAUUS = obj.SYCLAUUS
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
        dobj.SYCLCLWD = getattr(obj, '%s%d' % ('SYCLCWD', datestart.weekday()), 1)
        dobj.SYCLCLBD = getattr(obj, '%s%d' % ('SYCLCBD', datestart.weekday()), 1)
        dobj.SYCLCLPD = getattr(obj, '%s%d' % ('SYCLCPD', datestart.weekday()), 1)
        if not session.transaction_started():
          session.begin()
        try:
          session.update(dobj)
          session.commit()
        except:
          session.rollback()
          session.expunge(rec)
          raise
      datestart = datestart + dt.timedelta(1)



