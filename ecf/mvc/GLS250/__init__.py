"""
G/L Posting
"""

__author__    = 'Jaimy Azle'
__version__   = '1.0'
__copyright__ = 'Copyright (c) 2008 Jaimy Azle'

from mvcsvc import *
from elixir import *
import datetime as dt
from validators import *
import decimal as dcm
import sqlalchemy as sa
from jobsvc import jobassign
from tbl import GLSOPT, GLPOST, EFUSRS

class GLS250(MVCController):
  """
  G/L Posting
  """
  _description = 'G/L Posting'
  _supported_functions = (MVCFuncNew,)

  GLPODESC    = MVCField(MVCTypeField, String(48), label='Post Desc.')
  GLPOPOMO    = MVCField(MVCTypeField, Integer(), label='Type',
                  choices={
                      'All Batches':1,
                      'Batch Range':2
                  })
  GLPOBCFR    = MVCField(MVCTypeField, String(6), label='Range From', browseable=True)
  GLPOBCTO    = MVCField(MVCTypeField, String(6), label='To', browseable=True)
  GLPOPOTP    = MVCField(MVCTypeField, Integer(), label='Posting Mode',
                  choices={
                      'Normal Posting':1,
                      'Provisional Post':2
                  })

  def lookupView(self, session, fieldName):
    ret = MVCLookupDef('','')
    if fieldName == 'GLPOBCFR':
      ret.svcname = 'GLS100'
      ret.params = {'GLBCBST1': '%v:2'}
      ret.retfield = 'GLBCLSID'
    if fieldName == 'GLPOBCTO':
      ret.svcname = 'GLS100'
      ret.params = {'GLBCBST1': '%v:2'}
      ret.retfield = 'GLBCLSID'
    return ret

  def retrieveData(self, mvcsession):
    mvcsession.entryDataset.Append()
    mvcsession.entryDataset.SetFieldValue('GLPODESC', None)
    mvcsession.entryDataset.SetFieldValue('GLPOPOMO', 1)
    mvcsession.entryDataset.SetFieldValue('GLPOBCFR', None)
    mvcsession.entryDataset.SetFieldValue('GLPOBCTO', None)
    mvcsession.entryDataset.SetFieldValue('GLPOPOTP', 1)
    mvcsession.entryDataset.Post()
    return mvcsession

  def postData(self, mvcsession):
    proxy = self.getBusinessObjectProxy()
    usrobj = proxy.getObject('USROBJ')
    glsobj = proxy.getObject('GLSOBJ')
    info = usrobj.retrieveUserInfoDict(mvcsession)
    cono = info['USRCONO']
    glopt = glsobj.getGLOpt(cono)
    td = dt.datetime.now()
    fields = mvcsession.entryDataset.FieldsAsDict()
    if fields['GLPOPOMO'] == 2:
      validators.NotEmpty(messages={'empty': 'Batch from must not empty'}).to_python(fields['GLPOBCFR'])
      validators.NotEmpty(messages={'empty': 'Batch to must not empty'}).to_python(fields['GLPOBCTO'])

    # --- create job assignment ----
    job = jobassign.JOBAssignment()
    job.description = 'G/L Post: %s' % fields['GLPODESC']
    job.serviceName = 'GLS250'
    job.jobServiceName = 'JGLS250'
    job.user_name = mvcsession.cookies['user_name'].encode('utf8')
    # ----

    td = dt.datetime.now()
    obj = GLPOST(
      GLPOJBID    = job.jobID,
      GLPODESC    = fields['GLPODESC'],
      GLPOPOMO    = fields['GLPOPOMO'],
      GLPOCONO    = cono,
      GLPONOID    = glopt['GLOPBCNO'],
      GLPOBCFR    = fields['GLPOBCFR'],
      GLPOBCTO    = fields['GLPOBCTO'],
      GLPOPOTP    = fields['GLPOPOTP'],
      GLPOAUDT    = td.date().tointeger(),
      GLPOAUTM    = td.time().tointeger(),
      GLPOAUUS    = mvcsession.cookies['user_name'].encode('utf8')
    )

    if not session.transaction_started():
      session.begin()
    try:
      session.save(obj)
      session.commit()
    except:
      session.rollback()
      session.expunge(rec)
      raise
    # --- register job ---
    job.assignJob()
    # -----
    return mvcsession


