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

from mvcsvc import *
from elixir import *
import datetime as dt
import sqlalchemy as sa
from validators import *
from tbl import CMPLOC

class CMN125(MVCController):
  """
  Locations
  """

  _description = 'Locations'
  _supported_functions = (MVCFuncNew, MVCFuncOpen, MVCFuncShow, MVCFuncCopy, MVCFuncDelete)
  _model_binder = MVCModelBinder(CMPLOC)

  CMLOLCNO  = MVCField(MVCTypeField + MVCTypeList, String(3), label='Loc', charcase=ecUpperCase)
  CMLOLCNM  = MVCField(MVCTypeField + MVCTypeList, String(24), label='Name', synchronized=True)
  CMLOLCDS  = MVCField(MVCTypeField + MVCTypeList, String(48), label='Description')
  CMLOCONO  = MVCField(MVCTypeField, String(3), label='Comp. ID', enabled=False, visible=False)
  CMLODVNO  = MVCField(MVCTypeField + MVCTypeList, String(3), label='Division', synchronized=True, browseable=True, charcase = ecUpperCase)
  CMLODVNM  = MVCField(MVCTypeField + MVCTypeList, String(24), label='Division', enabled=False)
  CMLOADR1  = MVCField(MVCTypeField, String(48), label='Address')
  CMLOADR2  = MVCField(MVCTypeField, String(48), label='Address')
  CMLOADR3  = MVCField(MVCTypeField, String(48), label='Address')
  CMLOZIPC  = MVCField(MVCTypeField, String(48), label='Zip')
  CMLOARID  = MVCField(MVCTypeField, String(6), label='Area', synchronized=True, browseable=True, charcase = ecUpperCase)
  CMLOARNM  = MVCField(MVCTypeField, String(16), label='Area', enabled=False)
  CMLOSTID  = MVCField(MVCTypeField, String(6), label='State', synchronized=True, browseable=True, charcase = ecUpperCase)
  CMLOSTNM  = MVCField(MVCTypeField, String(16), label='State', enabled=False)
  CMLOCTID  = MVCField(MVCTypeField, String(2), label='Country', synchronized=True, browseable=True, charcase = ecUpperCase)
  CMLOCTNM  = MVCField(MVCTypeField, String(16), label='Country', enabled=False)
  CMLOPHN1  = MVCField(MVCTypeField, String(24), label='Phone')
  CMLOPHN2  = MVCField(MVCTypeField, String(24), label='Phone')
  CMLOFAX1  = MVCField(MVCTypeField, String(24), label='Fax')
  CMLOFAX2  = MVCField(MVCTypeField, String(24), label='Fax')
  CMLOXEML  = MVCField(MVCTypeField, String(32), label='email')
  CMLOWURL  = MVCField(MVCTypeField, String(48), label='URL')

  def lookupView(self, mvcsession, fieldName):
    '''Define lookup metadata for specified field'''
    ret = MVCLookupDef('','')
    if (fieldName == 'CMLODVNO'):
      ret.svcname = 'CMN110'
      ret.retfield = 'CMDVDVNO'
    if (fieldName == 'CMLOARID'):
      ret.svcname = 'CMN020'
      ret.retfield = 'CMARIDCD'
    if (fieldName == 'CMLOSTID'):
      ret.svcname = 'CMN030'
      ret.retfield = 'CMSTIDCD'
    if (fieldName == 'CMLOCTID'):
      ret.svcname = 'CMN010'
      ret.retfield = 'CMCTIDCD'
    return ret

  def synchronizeData(self, mvcsession, fieldName, fieldType):
    '''Synchronize data retrieved from user input'''
    fields = mvcsession.entryDataset.FieldsAsDict()
    proxy = self.getBusinessObjectProxy()
    if (fieldName == 'CMLOLCNM') and \
       (fields['CMLOLCNM'] is not None) and \
       (fields['CMLOLCDS'] is None):
      mvcsession.entryDataset.Edit()
      mvcsession.entryDataset.SetFieldValue('CMLOLCDS', fields['CMLOLCNM'])
      mvcsession.entryDataset.Post()
    elif (fieldName == 'CMLODVNO'):
      cmpobj = proxy.getObject('CMPOBJ')
      dvinfo = cmpobj.getDivision( fields['CMLOCONO'], fields['CMLODVNO'] )
      mvcsession.entryDataset.Edit()
      mvcsession.entryDataset.SetFieldValue('CMLOCONO', fields['CMLOCONO'])
      mvcsession.entryDataset.SetFieldValue('CMLODVNO', dvinfo[2])
      mvcsession.entryDataset.SetFieldValue('CMLODVNM', dvinfo[3])
      mvcsession.entryDataset.Post()
    elif (fieldName == 'CMLOARID'):
      cmpobj = proxy.getObject('CMPOBJ')
      arinfo = cmpobj.getArea( fields['CMLOARID'] )
      mvcsession.entryDataset.Edit()
      mvcsession.entryDataset.SetFieldValue('CMLOARID', arinfo[0])
      mvcsession.entryDataset.SetFieldValue('CMLOARNM', arinfo[1])
      mvcsession.entryDataset.Post()
    elif (fieldName == 'CMLOSTID'):
      cmpobj = proxy.getObject('CMPOBJ')
      stinfo = cmpobj.getState( fields['CMLOSTID'] )
      mvcsession.entryDataset.Edit()
      mvcsession.entryDataset.SetFieldValue('CMLOSTID', stinfo[0])
      mvcsession.entryDataset.SetFieldValue('CMLOSTNM', stinfo[1])
      mvcsession.entryDataset.Post()
    elif (fieldName == 'CMLOCTID'):
      cmpobj = proxy.getObject('CMPOBJ')
      ctinfo = cmpobj.getCountry( fields['CMLOSTID'] )
      mvcsession.entryDataset.Edit()
      mvcsession.entryDataset.SetFieldValue('CMLOSTID', ctinfo[0])
      mvcsession.entryDataset.SetFieldValue('CMLOCTNM', ctinfo[1])
      mvcsession.entryDataset.Post()
    return mvcsession

  def initializeData(self, mvcsession):
    '''Initializing data'''
    fields = {}
    proxy = self.getBusinessObjectProxy()
    usrobj = proxy.getObject('USROBJ')
    infodict = usrobj.retrieveUserInfoDict(mvcsession)
    fields['CMLOCONO'] = infodict['USRCONO']
    mvcsession.entryDataset.Append()
    mvcsession.entryDataset.SetFieldValues(fields)
    mvcsession.entryDataset.Post()
    return mvcsession


