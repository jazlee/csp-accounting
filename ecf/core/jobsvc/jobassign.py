import uuid
from elixir import *
import datetime as dt
from tbl import EFJBLS

class JOBAssignment(object):

  def __init__(self):
    self.assignmentDate = dt.datetime.now()
    self.uuid = uuid.uuid4()
    self.jobID = str(self.uuid)
    self.serviceName = None
    self.jobServiceName = None
    self.processDateTime = self.assignmentDate
    self.description = None
    self.user_name = None

  def assignJob(self):
    if self.serviceName == None:
      raise Exception('serviceName has not been assigned')
    if self.jobServiceName == None:
      raise Exception('jobServiceName has not been assigned')

    obj = EFJBLS.query.filter_by(JBLSIDNM = self.jobID).first()
    if obj:
      raise Exception('existing jobID has been existed')
    now = dt.datetime.now()
    rec = EFJBLS(
      JBLSIDNM = self.jobID,
      JBLSINDT = self.assignmentDate.date().tointeger(),
      JBLSINTM = self.assignmentDate.time().tointeger(),
      JBLSINID = self.description,
      JBLSRQPG = self.serviceName,
      JBLSRPDT = 0,
      JBLSRPTM = 0,
      JBLSPRPG = self.jobServiceName,
      JBLSPRST = 0,
      JBLSAUDT = now.date().tointeger(),
      JBLSAUTM = now.time().tointeger(),
      JBLSAUUS = self.user_name)
    if not session.transaction_started():
      session.begin()
    try:
      session.save(rec)
      session.commit()
    except:
      session.rollback()
      raise









