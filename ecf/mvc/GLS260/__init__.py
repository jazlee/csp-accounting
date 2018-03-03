"""
G/L Year End
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
from tbl import GLSOPT, GLYRED, EFUSRS

class GLS260(MVCController):
  """
  G/L Year End
  """
  _description = 'G/L Year End'
  _supported_functions = (MVCFuncNew,)

  GLYRDESC    = MVCField(MVCTypeField, String(48), label='Year End Desc.')
  GLYRFSYR    = MVCField(MVCTypeField, Integer(), label='Fiscal Year', browseable=True)

  def lookupView(self, mvcsession, fieldName):
    ret = MVCLookupDef('','')
    proxy = self.getBusinessObjectProxy()
    usrobj = proxy.getObject('USROBJ')
    glsobj = proxy.getObject('GLSOBJ')
    info = usrobj.retrieveUserInfoDict(mvcsession)
    cono = info['USRCONO']
    glopt = glsobj.getGLOpt(cono)
    if fieldName == 'GLYRFSYR':
      optvalue = '%v:'+ '%d' % glopt['GLOPFSTP']
      ret.svcname = 'CMN150'
      ret.params = {'SYFSFSTP': optvalue}
      ret.retfield = 'SYFSFSYR'
    return ret

  def retrieveData(self, mvcsession):
    proxy = self.getBusinessObjectProxy()
    usrobj = proxy.getObject('USROBJ')
    glsobj = proxy.getObject('GLSOBJ')
    info = usrobj.retrieveUserInfoDict(mvcsession)
    cono = info['USRCONO']
    glopt = glsobj.getGLOpt(cono)
    mvcsession.entryDataset.Append()
    mvcsession.entryDataset.SetFieldValue('GLYRDESC', None)
    mvcsession.entryDataset.SetFieldValue('GLYRFSYR', glopt['GLOPFSYR'])
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
    validators.NotEmpty(messages={'empty': 'Year field must not empty'}).to_python(fields['GLYRFSYR'])

    # --- create job assignmnet ----
    job = jobassign.JOBAssignment()
    job.description = 'G/L Year End: %s' % fields['GLYRDESC']
    job.serviceName = 'GLS260'
    job.jobServiceName = 'JGLS260'
    job.user_name = mvcsession.cookies['user_name'].encode('utf8')
    # ----

    td = dt.datetime.now()
    obj = GLYRED(
      GLYRJBID    = job.jobID,
      GLYRDESC    = fields['GLYRDESC'],
      GLYRCONO    = cono,
      GLYRFSTP    = glopt['GLOPFSTP'],
      GLYRFSYR    = fields['GLYRFSYR'],
      GLYRAUDT    = td.date().tointeger(),
      GLYRAUTM    = td.time().tointeger(),
      GLYRAUUS    = mvcsession.cookies['user_name'].encode('utf8')
    )

    if not session.transaction_started():
      session.begin()
    try:
      session.save(obj)
      session.commit()
    except:
      session.rollback()
      session.clear()
      raise
    # --- register job ---
    job.assignJob()
    # -----
    return mvcsession


