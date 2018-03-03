"""
G/L Create revaluation batch, this module purposed to hold initial data request
that required on performing Revaluation batch creation job process JGLS240.
by various modules on this system.
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
from tbl import GLSOPT, GLBCRV, EFUSRS, GLSCST, MSTCMP, GLSOPT

class GLS240(MVCController):
  """
  G/L Create revaluation batch, this module purposed to hold initial data request
  that required on performing Revaluation batch creation job process JGLS240.
  by various modules on this system.
  """

  _description = 'G/L Create Revaluation Batch'
  _supported_functions = (MVCFuncNew,)

  GLRVDESC    = MVCField(MVCTypeField, String(48), label='Reval Desc.')
  GLRVCRBC    = MVCField(MVCTypeField, Integer, label='Create new batch')
  GLRVBCID    = MVCField(MVCTypeField, String(6), label='Create in batch', browseable=True)
  GLRVCUCD    = MVCField(MVCTypeField, String(3), label='Currency', browseable=True)
  GLRVACTP    = MVCField(MVCTypeField, Integer, label='Revalue by',
                  choices = {
                    'Full Acct. No': 0,
                  }, synchronized = True)
  GLRVACAL    = MVCField(MVCTypeField, Integer, label='All Account')
  GLRVACFR    = MVCField(MVCTypeField, String(48), label='From', browseable=True)
  GLRVACTO    = MVCField(MVCTypeField, String(48), label='To', browseable=True)
  GLRVRVNM    = MVCField(MVCTypeField, String(6), label='Reval. Code', browseable=True)
  GLRVFSYR    = MVCField(MVCTypeField, Integer, label='Fiscal Year', browseable=True)
  GLRVFPFR    = MVCField(MVCTypeField, Integer, label='From Period', browseable=True)
  GLRVFPTO    = MVCField(MVCTypeField, Integer, label='To Period', browseable=True)
  GLRVJEDT    = MVCField(MVCTypeField, Date, label='JE Date')
  GLRVRTVL    = MVCField(MVCTypeField, Numeric(15, 4), label='Rate Value')
  GLRVRTDT    = MVCField(MVCTypeField, Date, label='Rate Date')
  GLRVFCRV    = MVCField(MVCTypeField, Integer, label='Force Reval')

  def initView(self, mvcsession):
    objs = GLSCST.query.all()
    for obj in objs:
      mvcsession.fieldDefs.GLRVACTP.choices[obj.CSCPCSNM] = obj.CSCPCSID
    return mvcsession

  def lookupView(self, mvcsession, fieldName):
    proxy = self.getBusinessObjectProxy()
    usrobj = proxy.getObject('USROBJ')
    glsobj = proxy.getObject('GLSOBJ')
    info = usrobj.retrieveUserInfoDict(mvcsession)
    cono = info['USRCONO']
    glopt = glsobj.getGLOpt(cono)

    ret = MVCLookupDef('','')
    fields = mvcsession.entryDataset.FieldsAsDict()
    if fieldName == 'GLRVCUCD':
      ret.svcname = 'CMN040'
      ret.retfield = 'CMCRCUCD'
    if fieldName == 'GLRVRVNM':
      ret.svcname = 'GLS080'
      ret.retfield = 'GLRVRVNM'
    if fieldName in ('GLRVFSYR', 'GLRVFPFR', 'GLRVFPTO'):
      if cono is None:
        cono = ''
      if cono == '':
        raise Exception('Default company for current user has not been setup')

      if glopt['GLOPFSTP'] is None:
        raise Exception('G/L Option has not been setup properly')

      optvalue = '%v:'+ '%d' % glopt['GLOPFSTP']
      if fieldName == 'GLRVFSYR':
        ret.svcname = 'CMN150'
        ret.params = {'SYFSFSTP': optvalue}
        ret.retfield = 'SYFSFSYR'
      elif fieldName in ('GLRVFPFR', 'GLRVFPTO'):
        ret.svcname = 'CMN155'
        ret.params = {'SYFPFSTP': optvalue, 'SYFPFSYR':'%f:GLRVFSYR'}
        ret.retfield = 'SYFPPRID'
    if fieldName == 'GLRVBCID':
      ret.svcname = 'GLS100'
      ret.params = {'GLBCBST1': '%v:1'}
      ret.retfield = 'GLBCLSID'
    if fieldName in ('GLRVACFR', 'GLRVACTO'):
      if fields['GLRVACTP'] == 0:
        ret.svcname = 'GLS450'
        ret.retfield = 'GLACACFM'
      else:
        ret.svcname = 'GLS020'
        ret.params = {'CSSICSID': '%f:GLRVACTP'}
        ret.retfield = 'CSSICSCD'
    return ret

  def retrieveData(self, mvcsession):
    proxy = self.getBusinessObjectProxy()
    usrobj = proxy.getObject('USROBJ')
    glsobj = proxy.getObject('GLSOBJ')
    info = usrobj.retrieveUserInfoDict(mvcsession)
    cono = info['USRCONO']
    glopt = glsobj.getGLOpt(cono)
    cmpobj = proxy.getObject('CMPOBJ')
    fscobj = proxy.getObject('FSCOBJ')

    if cono is None:
      cono = ''
    if cono == '':
      raise Exception('Default company for current user has not been setup')

    mstcmp = cmpobj.getCompany(cono)
    if mstcmp[1] is None:
      raise Exception('Company has not been setup properly')

    if glopt['GLOPFSTP'] is None:
      raise Exception('G/L Option has not been setup properly')

    prd = fscobj.getMinMaxPeriod(cono, glopt['GLOPFSTP'], glopt['GLOPFSYR'])
    if prd is None:
      raise Exception('Fiscal period has not been setup properly')

    mvcsession.entryDataset.Append()
    mvcsession.entryDataset.SetFieldValue('GLRVDESC', None)
    mvcsession.entryDataset.SetFieldValue('GLRVCRBC', 0)
    mvcsession.entryDataset.SetFieldValue('GLRVBCID', None)
    mvcsession.entryDataset.SetFieldValue('GLRVCUCD', None)
    mvcsession.entryDataset.SetFieldValue('GLRVACTP', 0)
    mvcsession.entryDataset.SetFieldValue('GLRVACAL', 0)
    mvcsession.entryDataset.SetFieldValue('GLRVACFR', None)
    mvcsession.entryDataset.SetFieldValue('GLRVACTO', None)
    mvcsession.entryDataset.SetFieldValue('GLRVRVNM', None)
    mvcsession.entryDataset.SetFieldValue('GLRVFSYR', glopt['GLOPFSYR'])
    mvcsession.entryDataset.SetFieldValue('GLRVFPFR', prd[0])
    mvcsession.entryDataset.SetFieldValue('GLRVFPTO', prd[1])
    mvcsession.entryDataset.SetFieldValue('GLRVJEDT', dt.date.today().tointeger())
    mvcsession.entryDataset.SetFieldValue('GLRVRTVL', 0)
    mvcsession.entryDataset.SetFieldValue('GLRVRTDT', dt.date.today().tointeger())
    mvcsession.entryDataset.SetFieldValue('GLRVFCRV', 0)
    mvcsession.entryDataset.Post()
    return mvcsession

  def postData(self, mvcsession):
    proxy = self.getBusinessObjectProxy()
    usrobj = proxy.getObject('USROBJ')
    glsobj = proxy.getObject('GLSOBJ')
    info = usrobj.retrieveUserInfoDict(mvcsession)
    cono = info['USRCONO']
    glopt = glsobj.getGLOpt(cono)
    cmpobj= proxy.getObject('CMPOBJ')
    if cono is None:
      cono = ''
    if cono == '':
      raise Exception('Default company for current user has not been setup')
    mstcmp = cmpobj.getCompany(cono)
    if mstcmp[0] is None:
      raise Exception('Company has not been setup properly')

    if glopt['GLOPFSTP'] is None:
      raise Exception('G/L Option has not been setup properly')

    td = dt.datetime.now()
    fields = mvcsession.entryDataset.FieldsAsDict()
    if fields['GLRVCRBC'] == 0:
      validators.NotEmpty(messages={'empty': 'batch id must not empty'}).to_python(fields['GLRVBCID'])
    validators.NotEmpty(messages={'empty': 'currency code must not empty'}).to_python(fields['GLRVCUCD'])
    if fields['GLRVACAL'] == 0:
      validators.NotEmpty(messages={'empty': 'Account from must not empty'}).to_python(fields['GLRVACFR'])
      validators.NotEmpty(messages={'empty': 'Account to must not empty'}).to_python(fields['GLRVACTO'])
    validators.NotEmpty(messages={'empty': 'Reval code must not empty'}).to_python(fields['GLRVRVNM'])

    # --- create job assignment ----
    job = jobassign.JOBAssignment()
    job.description = 'G/L Revaluation: %s' % fields['GLRVDESC']
    job.serviceName = 'GLS240'
    job.jobServiceName = 'JGLS240'
    job.user_name = mvcsession.cookies['user_name'].encode('utf8')
    # ----

    td = dt.datetime.now()
    obj = GLBCRV()
    obj.GLRVJBID    = job.jobID
    obj.GLRVDESC    = fields['GLRVDESC']
    obj.GLRVCONO    = cono
    obj.GLRVCRBC    = fields['GLRVCRBC']
    obj.GLRVBCID    = fields['GLRVBCID']
    obj.GLRVCUCD    = fields['GLRVCUCD']
    obj.GLRVACTP    = fields['GLRVACTP']
    obj.GLRVACAL    = fields['GLRVACAL']
    obj.GLRVACFR    = fields['GLRVACFR']
    obj.GLRVACTO    = fields['GLRVACTO']
    obj.GLRVRVNM    = fields['GLRVRVNM']
    obj.GLRVFSTP    = glopt['GLOPFSTP']
    obj.GLRVFSYR    = fields['GLRVFSYR']
    obj.GLRVFPFR    = fields['GLRVFPFR']
    obj.GLRVFPTO    = fields['GLRVFPTO']
    obj.GLRVJEDT    = fields['GLRVJEDT'].date().tointeger()
    obj.GLRVRTVL    = fields['GLRVRTVL']
    obj.GLRVRTDT    = fields['GLRVRTDT'].date().tointeger()
    obj.GLRVFCRV    = fields['GLRVFCRV']
    obj.GLRVAUDT    = td.date().tointeger()
    obj.GLRVAUTM    = td.time().tointeger()
    obj.GLRVAUUS    = mvcsession.cookies['user_name'].encode('utf8')

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


