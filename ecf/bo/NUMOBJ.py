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
from tbl import NUMTYP, NUMSER

class NUMOBJ(BusinessObject):
  """
  Numbering series object collection
  """

  def getNumberingCode(self, cono, numtyp):
    cono = '' if cono is None else cono
    numtyp = '' if numtyp is None else numtyp
    obj = NUMTYP.get( (cono, numtyp) )
    if obj:
      return (obj.NMTPNOID, obj.NMTPNONM)
    return (None, None)

  def checkNumberingCode(self, cono, numtyp):
    numinfo = self.getNumberingCode(cono,  numtyp)
    if numinfo[0] is None:
      raise Exception("Numbering type is not valid")

  def getLastNumber(self, cono, numtyp, frdt):
    cono = '' if cono is None else cono
    numtyp = '' if numtyp is None else numtyp
    numinfo = self.getNumberingCode(cono, numtyp)
    if numinfo[0] is None:
      raise Exception('Numbering code is not defined')
    q = NUMSER.query
    q = q.filter_by(NMSRCONO = cono)
    q = q.filter_by(NMSRNOID = numtyp)
    q = q.filter(NUMSER.NMSRFRDT <= frdt)
    q = q.order_by(sa.asc(NUMSER.NMSRCONO))
    q = q.order_by(sa.asc(NUMSER.NMSRNOID))
    q = q.order_by(sa.desc(NUMSER.NMSRFRDT))
    obj = q.first()

    if not obj:
      raise Exception('numbering series does not exist')

    lsno = obj.NMSRMINO if (obj.NMSRLSNO is None) or \
            (obj.NMSRMINO > obj.NMSRLSNO) else \
            obj.NMSRLSNO + 1

    if lsno > obj.NMSRMXNO:
      raise Exception('Maximum number has been reached')

    prefix = (obj.NMSRPFCD if obj.NMSRPFCD is not None else '')[:3]
    suffix = (obj.NMSRSFCD if obj.NMSRSFCD is not None else '')[:3]
    numlen = 12 - (len(prefix) + len(suffix))
    strfmt = '%%s%%.%dd%%s' % numlen
    numfmt = strfmt % (prefix, lsno, suffix)

    obj.NMSRLSNO = lsno

    session.update(obj)

    return (obj.NMSRCONO, obj.NMSRNOID, obj.NMSRFRDT, numfmt, \
            obj.NMSRLSNO, obj.NMSRMINO, obj.NMSRMXNO)
