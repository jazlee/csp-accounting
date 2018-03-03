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
from jitutil import *
import datetime as dt
import sqlalchemy as sa
from tbl import EFSYVR
from mvcsvc import MVCTypeParam

@nativeclass
class SYSOBJ(BusinessObject):
  """
  System Object collection
  """

  def getPGMVar(self, cono, mvcsession):
    query = EFSYVR.query.filter_by(EFSYCONO = cono)
    query = query.filter_by(EFSYUSID = mvcsession.cookies['user_name'].encode('utf8'))
    query = query.filter_by(EFSYPGID = mvcsession.program)
    objs = query.all()
    _dict = dict()
    for fieldDef in mvcsession.getFieldDefs():
      if (fieldDef[3] & MVCTypeParam) == MVCTypeParam:
        _dict[fieldDef[1]] = [None for i in range(0, 10, 1)]
    if objs:
      for obj in objs:
        ab = [getattr(obj, 'EFSYVRV%d' % i) for i in range(0, 10, 1)]
        if _dict.has_key(obj.EFSYVRID):
          _dict[obj.EFSYVRID] = ab
    return _dict

  def setPGMVar(self, cono, mvcsession):
    paramFields = [fieldDef[1] for fieldDef in mvcsession.getFieldDefs() \
      if (fieldDef[3] & MVCTypeParam) == MVCTypeParam]
    _dict = dict()
    fields = mvcsession.paramDataset.FieldsAsDict()
    for paramField in paramFields:
      _dict[paramField] = [None] * 10
      if (fields[paramField] != None):
        _dict[paramField][0] = str(fields[paramField]) if fields[paramField] != None else None
    self.setPGMVarDict(cono, mvcsession, _dict)

  def setPGMVarDict(self, cono, mvcsession, _dict):
    if not session.transaction_started():
      session.begin()
    try:
      for key, value in _dict.iteritems():
        lappend = True
        obj = EFSYVR.get( (cono, mvcsession.cookies['user_name'].encode('utf8'),
                        mvcsession.program, key) )
        if obj:
          lappend = False
        if lappend:
          obj = EFSYVR(
                  EFSYCONO  = cono,
                  EFSYUSID  = mvcsession.cookies['user_name'].encode('utf8'),
                  EFSYPGID  = mvcsession.program,
                  EFSYVRID  = key
                )
        for i in range(0, 10, 1):
          setattr(obj, 'EFSYVRV%d' % i, value[i])
        if lappend:
          session.add(obj)
        else:
          session.update(obj)
      session.commit()
    except:
      session.rollback()
      raise

  def initDatabase(self):
    """
    Initialize database
    """
    # compile_package('sqlalchemy')
    pass
