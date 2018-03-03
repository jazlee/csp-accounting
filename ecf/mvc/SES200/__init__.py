"""
ECF Job List
"""

__author__    = 'Jaimy Azle'
__version__   = '1.0'
__copyright__ = 'Copyright (c) 2008 Jaimy Azle'

from elixir import *
from mvcsvc import *
import sqlalchemy as sa
from sqlalchemy import sql
from sqlalchemy.sql import operators
import datetime as dt
from validators import *
from tbl import EFJBLS

class SES200(MVCController):
  """
  ECF Job List
  """
  _description = 'ECF Job list'

  JBLSIDNM    = MVCField(MVCTypeList, String(38), label='Job ID')
  JBLSINID    = MVCField(MVCTypeList, String(38), label='Desc')
  JBLSPRPG    = MVCField(MVCTypeList, String(24), label='Job Name')
  JBLSAUUS    = MVCField(MVCTypeList, String(24), label='Req. By')
  JBLSINDT    = MVCField(MVCTypeList, Numeric(8,0), label='Req. Date')
  JBLSINTM    = MVCField(MVCTypeList, Numeric(6,0), label='Req. Time')
  JBLSPRDT    = MVCField(MVCTypeList, Numeric(8,0), label='Proc.Date')
  JBLSPRTM    = MVCField(MVCTypeList, Numeric(6,0), label='Proc.Time')
  JBLSPRST    = MVCField(MVCTypeList + MVCTypeParam, Integer(), label='Status',
    choices={
              'All jobs':-1,
              'Unproceeded':0,
              'Proceeded':10,
              'Failed':99,
              'Completed':100
            })
  JBLSPRMS    = MVCField(MVCTypeList, String(64), label='Message')

  def openView(self, mvcsession):
    if mvcsession.paramDataset.RecordCount == 0:
      mvcsession.paramDataset.Append()
      mvcsession.paramDataset.SetFieldValue('JBLSPRST', -1)
      mvcsession.paramDataset.Post()

    today = dt.datetime.now()
    begindate = today.date() - dt.timedelta(30)
    enddate = today.date()
    params = mvcsession.paramDataset.FieldsAsDict()
    q = EFJBLS.query
    q = q.filter(sql.and_(
          EFJBLS.JBLSINDT >= begindate.tointeger(),
          EFJBLS.JBLSINDT <= enddate.tointeger()
         )
        )
    if params['JBLSPRST'] != -1:
      q = q.filter_by(JBLSPRST = params['JBLSPRST'])
    q = q.order_by(sa.desc(EFJBLS.JBLSINDT))
    q = q.order_by(sa.desc(EFJBLS.JBLSINTM))
    obj = q.all()
    mvcsession.listDataset.CopyFromORMList(
      'JBLSIDNM;JBLSINID;JBLSINDT;JBLSINTM;JBLSPRDT;JBLSPRTM;JBLSPRPG;JBLSAUUS;JBLSPRST;JBLSPRMS',
      'JBLSIDNM;JBLSINID;JBLSINDT;JBLSINTM;JBLSPRDT;JBLSPRTM;JBLSPRPG;JBLSAUUS;JBLSPRST;JBLSPRMS',
      obj
      )
    return mvcsession

