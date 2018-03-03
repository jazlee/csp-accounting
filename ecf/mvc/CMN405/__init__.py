"""
Create System Calendar, this module purposed for requesting System Calendar
creation which will be done by job JCMN175.
"""
__author__    = 'Jaimy Azle'
__version__   = '1.0'
__copyright__ = 'Copyright (c) 2008 Jaimy Azle'

from mvcsvc import *
from elixir import *
import datetime as dt
import sqlalchemy as sa
from validators import *
# job assignment utility
from jobsvc import jobassign
from tbl import SYSCLJ

class CMN405(MVCController):
  """
  Create System Calendar, this module purposed for requesting System Calendar
  creation which will be done by job JCMN175.
  """

  _description = 'Create System Calendar'
  _supported_functions = (MVCFuncNew, )

  SYCLCONO    = MVCField(MVCTypeField + MVCTypeParam, String(3), label='Comp. ID',
                  enabled=False, visible=False)
  SYCLCLYR    = MVCField(MVCTypeField, Numeric(4), label='Year')
  SYCLCLDS    = MVCField(MVCTypeField, String(48), label='Description')
  SYCLCWD0    = MVCField(MVCTypeField, Integer(), label='Work day')
  SYCLCBD0    = MVCField(MVCTypeField, Integer(), label='Bank day')
  SYCLCPD0    = MVCField(MVCTypeField, Integer(), label='Pay day')
  SYCLCWD1    = MVCField(MVCTypeField, Integer(), label='Work day')
  SYCLCBD1    = MVCField(MVCTypeField, Integer(), label='Bank day')
  SYCLCPD1    = MVCField(MVCTypeField, Integer(), label='Pay day')
  SYCLCWD2    = MVCField(MVCTypeField, Integer(), label='Work day')
  SYCLCBD2    = MVCField(MVCTypeField, Integer(), label='Bank day')
  SYCLCPD2    = MVCField(MVCTypeField, Integer(), label='Pay day')
  SYCLCWD3    = MVCField(MVCTypeField, Integer(), label='Work day')
  SYCLCBD3    = MVCField(MVCTypeField, Integer(), label='Bank day')
  SYCLCPD3    = MVCField(MVCTypeField, Integer(), label='Pay day')
  SYCLCWD4    = MVCField(MVCTypeField, Integer(), label='Work day')
  SYCLCBD4    = MVCField(MVCTypeField, Integer(), label='Bank day')
  SYCLCPD4    = MVCField(MVCTypeField, Integer(), label='Pay day')
  SYCLCWD5    = MVCField(MVCTypeField, Integer(), label='Work day')
  SYCLCBD5    = MVCField(MVCTypeField, Integer(), label='Bank day')
  SYCLCPD5    = MVCField(MVCTypeField, Integer(), label='Pay day')
  SYCLCWD6    = MVCField(MVCTypeField, Integer(), label='Work day')
  SYCLCBD6    = MVCField(MVCTypeField, Integer(), label='Bank day')
  SYCLCPD6    = MVCField(MVCTypeField, Integer(), label='Pay day')

  def retrieveData(self, mvcsession):
    proxy = self.getBusinessObjectProxy()
    usrobj = proxy.getObject('USROBJ')
    infodict = usrobj.retrieveUserInfoDict(mvcsession)

    cmpobj = proxy.getObject('CMPOBJ')
    cmpobj.validateCompany(infodict['USRCONO'])

    today = dt.date.today()
    q = SYSCLJ.query
    q = q.filter_by(SYCLCONO = infodict['USRCONO'])
    q = q.filter_by(SYCLCLYR = today.year)
    obj = q.first()
    if obj:
      mvcsession.entryDataset.CopyFromORM(
          'SYCLCONO;SYCLCLYR;SYCLCLDS;SYCLCWD0;SYCLCBD0;SYCLCPD0;SYCLCWD1;SYCLCBD1;SYCLCPD1;SYCLCWD2;SYCLCBD2;SYCLCPD2;SYCLCWD3;SYCLCBD3;SYCLCPD3;SYCLCWD4;SYCLCBD4;SYCLCPD4;SYCLCWD5;SYCLCBD5;SYCLCPD5;SYCLCWD6;SYCLCBD6;SYCLCPD6',
          'SYCLCONO;SYCLCLYR;SYCLCLDS;SYCLCWD0;SYCLCBD0;SYCLCPD0;SYCLCWD1;SYCLCBD1;SYCLCPD1;SYCLCWD2;SYCLCBD2;SYCLCPD2;SYCLCWD3;SYCLCBD3;SYCLCPD3;SYCLCWD4;SYCLCBD4;SYCLCPD4;SYCLCWD5;SYCLCBD5;SYCLCPD5;SYCLCWD6;SYCLCBD6;SYCLCPD6',
          obj
        )
    else:
      mvcsession.entryDataset.Append()
      mvcsession.entryDataset.SetFieldValue('SYCLCONO', infodict['USRCONO'])
      mvcsession.entryDataset.SetFieldValue('SYCLCLYR', today.year)
      mvcsession.entryDataset.SetFieldValue('SYCLCLDS', 'Calendar #%d' % today.year)
      mvcsession.entryDataset.SetFieldValue('SYCLCWD0', 1)
      mvcsession.entryDataset.SetFieldValue('SYCLCBD0', 1)
      mvcsession.entryDataset.SetFieldValue('SYCLCPD0', 1)
      mvcsession.entryDataset.SetFieldValue('SYCLCWD1', 1)
      mvcsession.entryDataset.SetFieldValue('SYCLCBD1', 1)
      mvcsession.entryDataset.SetFieldValue('SYCLCPD1', 1)
      mvcsession.entryDataset.SetFieldValue('SYCLCWD2', 1)
      mvcsession.entryDataset.SetFieldValue('SYCLCBD2', 1)
      mvcsession.entryDataset.SetFieldValue('SYCLCPD2', 1)
      mvcsession.entryDataset.SetFieldValue('SYCLCWD3', 1)
      mvcsession.entryDataset.SetFieldValue('SYCLCBD3', 1)
      mvcsession.entryDataset.SetFieldValue('SYCLCPD3', 1)
      mvcsession.entryDataset.SetFieldValue('SYCLCWD4', 1)
      mvcsession.entryDataset.SetFieldValue('SYCLCBD4', 1)
      mvcsession.entryDataset.SetFieldValue('SYCLCPD4', 1)
      mvcsession.entryDataset.SetFieldValue('SYCLCWD5', 1)
      mvcsession.entryDataset.SetFieldValue('SYCLCBD5', 1)
      mvcsession.entryDataset.SetFieldValue('SYCLCPD5', 1)
      mvcsession.entryDataset.SetFieldValue('SYCLCWD6', 0)
      mvcsession.entryDataset.SetFieldValue('SYCLCBD6', 0)
      mvcsession.entryDataset.SetFieldValue('SYCLCPD6', 0)
      mvcsession.entryDataset.Post()
    return mvcsession

  def postData(self, mvcsession):
    proxy = self.getBusinessObjectProxy()
    fields = mvcsession.entryDataset.FieldsAsDict()
    validators.NotEmpty(messages={'empty': 'Calendar year must not empty'}).to_python(fields['SYCLCLYR'])

    cmpobj = proxy.getObject('CMPOBJ')
    cmpobj.validateCompany(fields['SYCLCONO'])

    q = SYSCLJ.query
    q = q.filter_by(SYCLCONO = fields['SYCLCONO'])
    q = q.filter_by(SYCLCLYR = fields['SYCLCLYR'])
    obj = q.first()

    # --- create job assignmnet ----
    job = jobassign.JOBAssignment()
    job.description = 'Create Cal #%d' % fields['SYCLCLYR']
    job.serviceName = 'CMN405'
    job.jobServiceName = 'JCMN405'
    job.user_name = mvcsession.cookies['user_name'].encode('utf8')
    # ----

    td = dt.datetime.now()
    if not obj:
      rec = SYSCLJ(
              SYCLCONO   =  fields['SYCLCONO'],
              SYCLCLYR   =  fields['SYCLCLYR'],
              SYCLCLDS   =  fields['SYCLCLDS'],
              SYCLCWD0   =  fields['SYCLCWD0'],
              SYCLCBD0   =  fields['SYCLCBD0'],
              SYCLCPD0   =  fields['SYCLCPD0'],
              SYCLCWD1   =  fields['SYCLCWD1'],
              SYCLCBD1   =  fields['SYCLCBD1'],
              SYCLCPD1   =  fields['SYCLCPD1'],
              SYCLCWD2   =  fields['SYCLCWD2'],
              SYCLCBD2   =  fields['SYCLCBD2'],
              SYCLCPD2   =  fields['SYCLCPD2'],
              SYCLCWD3   =  fields['SYCLCWD3'],
              SYCLCBD3   =  fields['SYCLCBD3'],
              SYCLCPD3   =  fields['SYCLCPD3'],
              SYCLCWD4   =  fields['SYCLCWD4'],
              SYCLCBD4   =  fields['SYCLCBD4'],
              SYCLCPD4   =  fields['SYCLCPD4'],
              SYCLCWD5   =  fields['SYCLCWD5'],
              SYCLCBD5   =  fields['SYCLCBD5'],
              SYCLCPD5   =  fields['SYCLCPD5'],
              SYCLCWD6   =  fields['SYCLCWD6'],
              SYCLCBD6   =  fields['SYCLCBD6'],
              SYCLCPD6   =  fields['SYCLCPD6'],
              SYCLJBID   =  job.jobID,
              SYCLAUDT   =  td.date().tointeger(),
              SYCLAUTM   =  td.time().tointeger(),
              SYCLAUUS   =  mvcsession.cookies['user_name'].encode('utf8')
            )
      if not session.transaction_started():
        session.begin()
      try:
        session.add(rec)
        session.commit()
      except:
        session.rollback()
        session.expunge(rec)
        raise
    else:
      obj.SYCLCLDS   =  fields['SYCLCLDS']
      obj.SYCLCWD0   =  fields['SYCLCWD0']
      obj.SYCLCBD0   =  fields['SYCLCBD0']
      obj.SYCLCPD0   =  fields['SYCLCPD0']
      obj.SYCLCWD1   =  fields['SYCLCWD1']
      obj.SYCLCBD1   =  fields['SYCLCBD1']
      obj.SYCLCPD1   =  fields['SYCLCPD1']
      obj.SYCLCWD2   =  fields['SYCLCWD2']
      obj.SYCLCBD2   =  fields['SYCLCBD2']
      obj.SYCLCPD2   =  fields['SYCLCPD2']
      obj.SYCLCWD3   =  fields['SYCLCWD3']
      obj.SYCLCBD3   =  fields['SYCLCBD3']
      obj.SYCLCPD3   =  fields['SYCLCPD3']
      obj.SYCLCWD4   =  fields['SYCLCWD4']
      obj.SYCLCBD4   =  fields['SYCLCBD4']
      obj.SYCLCPD4   =  fields['SYCLCPD4']
      obj.SYCLCWD5   =  fields['SYCLCWD5']
      obj.SYCLCBD5   =  fields['SYCLCBD5']
      obj.SYCLCPD5   =  fields['SYCLCPD5']
      obj.SYCLCWD6   =  fields['SYCLCWD6']
      obj.SYCLCBD6   =  fields['SYCLCBD6']
      obj.SYCLCPD6   =  fields['SYCLCPD6']
      obj.SYCLJBID   =  job.jobID
      obj.SYCLAUDT   =  td.date().tointeger()
      obj.SYCLAUTM   =  td.time().tointeger()
      obj.SYCLAUUS   =  mvcsession.cookies['user_name'].encode('utf8')

      if not session.transaction_started():
        session.begin()
      try:
        session.update(obj)
        session.commit()
      except:
        session.rollback()
        session.expunge(obj)
        raise

    # --- register job ---
    job.assignJob()
    # -----
    return mvcsession



