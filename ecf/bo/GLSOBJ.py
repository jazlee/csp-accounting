#
# Copyright (c) 2009 Cipta Solusi Pratama. All rights reserved.
#
# This product and it's source code is protected by patents, copyright laws and
# international copyright treaties, as well as other intellectual property
# laws and treaties. The product is licensed, not sold.
#
# The source code and sample programs in this package or parts hereof
# as well as the documentation shall not be copied, modified or redistributed
# without permission, explicit or implied, of the author.
#

__author__    = 'Jaimy Azle'
__version__   = '1.0'
__copyright__ = 'Copyright (c) 2009 Cipta Solusi Pratama'

from procsvc import *
from elixir import *
from validators import *
import datetime as dt
import sqlalchemy as sa
from sqlalchemy.orm.attributes import InstrumentedAttribute
import re
import ecfpool
from tbl import GLACCT, GLSOPT, GLSACS, GLSACI, GLSCST, GLSCSI
from tbl import GLSRCE

class GLSOBJ(BusinessObject):
  """
  G/L Business Objects
  """

  def expandGLSourceCode(self, src):
    if src == 'SR-CD':
      raise Exception('Source code should not be an example one')
    splitted = None
    if len(src) == 5:
      splitted = src.split('-')
      if (len(splitted) != 2) or (len(splitted[0]) != 2) or (len(splitted[1]) != 2):
        raise Exception('Length of \'SOURCE\' and \'TYPE\' must be in 2 digit code separated by \'-\'.')
      glcode = "%s%s" % tuple(splitted)
      splitted.append(glcode)
    else:
      raise Exception('Source code must be in 5 digit code')
    return splitted

  def formatacct(self, defcono, structure, acct):
    pre = re.compile('\w+')
    acctvalue = ''.join(pre.findall(acct))
    opt = GLSOPT.query.filter_by(GLOPCONO = defcono).first()
    if not opt:
      raise Exception('GL Option has not been setup')
    sobjs = GLSACI.query.filter_by(AIASACCD = structure).order_by(sa.asc(GLSACI.AIASCSIX)).all()
    if not sobjs:
      raise Exception('Default account structure has not been setup properly')
    alst = []
    for sobj in sobjs:
      gobj = GLSCST.query.filter_by(CSCPCSID = sobj.AIASCSID).first()
      if not gobj:
        raise Exception('Cluster used in structure has not been setup properly')
      alst.append((gobj.CSCPCSID, gobj.CSCPCSLN))

    fmtvalue = ''
    lstvalue = [fmtvalue, ]
    for (csid, cslen) in alst:
      csvalue = acctvalue[:cslen]
      acctvalue = acctvalue[cslen:]
      if (len(fmtvalue) > 0) and (len(csvalue) > 0):
        fmtvalue += opt.GLOPACDL
      fmtvalue += csvalue
      lstvalue.append((csid, csvalue))
    lstvalue[0] = fmtvalue

    return tuple(lstvalue)

  def stripedacct(self, acct):
    pre = re.compile('\w+')
    vacct = ''.join(pre.findall(acct)) if acct not in (None, '') else None
    return vacct

  def acctexists(self, cono, acct):
    ret = [False, None]
    q = GLACCT.query.filter_by(GLACCONO = cono)
    q = q.filter_by(GLACACID = acct)
    obj = q.filter_by(GLACACST = 1).first()
    if (obj is not None):
      ret[0] = True
      ret[1] = GLACCT.formatacct(cono, obj.GLACSTID, acct)
    return tuple(ret)

  def getFieldList(self, cls):
    fieldlist = [(key, None) for key in cls.__dict__.keys() \
      if isinstance(cls.__dict__[key], InstrumentedAttribute)]
    return dict(fieldlist)

  def setFieldValues(self, adict, obj):
    for key in adict.keys():
      adict[key] = getattr(obj, key, None)

  def getAcct(self, cono, acctid):
    retfield = self.getFieldList(GLACCT)
    acct = self.stripedacct(acctid)
    q = GLACCT.query.filter_by(GLACCONO = cono, GLACACID = acct)
    obj = q.first()
    self.setFieldValues(retfield,  obj)
    return retfield

  def getAcctStructure(self, aCode):
    retfield = self.getFieldList(GLSACS)
    obj = GLSACS.query.filter_by(ACASACCD = aCode).first()
    self.setFieldValues(retfield,  obj)
    return retfield

  def getAcctCluster(self, aCode):
    retfield = self.getFieldList(GLSCST)
    obj = GLSCST.query.filter_by(CSCPCSID = aCode).first()
    self.setFieldValues(retfield,  obj)
    return retfield

  def getGLOpt(self, cono):
    retfield = self.getFieldList(GLSOPT)
    obj = GLSOPT.query.filter_by(GLOPCONO = cono).first()
    if obj is None:
      raise Exception('G/L Option has not been setup properly')
    self.setFieldValues(retfield,  obj)
    return retfield

