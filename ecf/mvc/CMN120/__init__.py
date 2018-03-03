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
from tbl import CMPFAC

class CMN120(MVCController):
  """
  Company Connect Facilities
  """

  _description = 'Company Connect Facilities'
  _supported_functions = (MVCFuncNew, MVCFuncOpen, MVCFuncShow, MVCFuncCopy, MVCFuncDelete)
  _model_binder = MVCModelBinder(CMPFAC)

  CMFAFANO  = MVCField(MVCTypeField+MVCTypeList, String(3), label='Facility', charcase = ecUpperCase)
  CMFAFANM  = MVCField(MVCTypeField+MVCTypeList, String(24), label='Name', synchronized=True)
  CMFAFADS  = MVCField(MVCTypeField, String(48), label='Description')
  CMFACONO  = MVCField(MVCTypeField+MVCTypeList, String(3), label='Company', synchronized=True, browseable=True, charcase = ecUpperCase)
  CMFACONM  = MVCField(MVCTypeField, String(24), label='Company Name', enabled=False)
  CMFADVNO  = MVCField(MVCTypeField+MVCTypeList, String(3), label='Division', synchronized=True, browseable=True, charcase = ecUpperCase)
  CMFADVNM  = MVCField(MVCTypeField, String(24), label='Division', enabled=False)
  CMFAGFNO  = MVCField(MVCTypeField, String(3), label='Global facility', synchronized=True, browseable=True, charcase = ecUpperCase)
  CMFAGFNM  = MVCField(MVCTypeField, String(24), label='Global facility', enabled=False)

  def initView(self, mvcsession):
    '''Initialize the program'''
    mvcsession.extFunctions = ( MVCExtFunction('Company Identification', 'CMN100'),
      MVCExtFunction('Locations', 'CMN125'),
    )
    return mvcsession


  def lookupView(self, mvcsession, fieldName):
    '''Define lookup metadata for specified field'''
    ret = MVCLookupDef('','')
    if (fieldName == 'CMFACONO'):
      ret.svcname = 'CMN100'
      ret.retfield = 'CMCPCONO'
    elif (fieldName == 'CMFAGFNO'):
      ret.svcname = 'CMN120'
      ret.retfield = 'CMFAFANO'
    elif (fieldName == 'CMFADVNO'):
      ret.svcname = 'CMN110'
      ret.retfield = 'CMDVDVNO'
      ret.extassignment = {'CMFACONO':'%f:CMDVCONO'} if (fieldName == 'CMFADVNO') else \
        {'PRFADVNO':'%f:CMDVDVNO'}
    return ret

  def synchronizeData(self, mvcsession, fieldName, fieldType):
    '''Synchronize data retrieved from user input'''
    fields = mvcsession.entryDataset.FieldsAsDict()
    proxy = self.getBusinessObjectProxy()
    if (fieldName == 'CMFAFANM') and (fields['CMFAFANM'] is not None) and \
       (fields['CMFAFADS'] is None):
      mvcsession.entryDataset.Edit()
      mvcsession.entryDataset.SetFieldValue('CMFAFADS', fields['CMFAFANM'])
      mvcsession.entryDataset.Post()
    elif (fieldName == 'CMFACONO'):
      cmpobj = proxy.getObject('CMPOBJ')
      restuple = cmpobj.getCompany( fields['CMFACONO'] )
      mvcsession.entryDataset.Edit()
      mvcsession.entryDataset.SetFieldValue('CMFACONO', restuple[0])
      mvcsession.entryDataset.SetFieldValue('CMFACONM', restuple[1])
      mvcsession.entryDataset.Post()
    elif (fieldName == 'CMFADVNO'):
      cmpobj = proxy.getObject('CMPOBJ')
      restuple = cmpobj.getDivision( fields['CMFACONO'], fields['CMFADVNO'] )
      mvcsession.entryDataset.Edit()
      mvcsession.entryDataset.SetFieldValue('CMFACONO', restuple[0])
      mvcsession.entryDataset.SetFieldValue('CMFACONM', restuple[1])
      mvcsession.entryDataset.SetFieldValue('CMFADVNO', restuple[2])
      mvcsession.entryDataset.SetFieldValue('CMFADVNM', restuple[3])
      mvcsession.entryDataset.Post()
    elif (fieldName == 'CMFAGFNO'):
      cmpobj = proxy.getObject('CMPOBJ')
      restuple = cmpobj.getFacility( fields['CMFAGFNO'] )
      mvcsession.entryDataset.Edit()
      mvcsession.entryDataset.SetFieldValue('CMFAGFNO', restuple[4])
      mvcsession.entryDataset.SetFieldValue('CMFAGFNM', restuple[5])
      mvcsession.entryDataset.Post()
    return mvcsession

  def initializeData(self, mvcsession):
    '''Initializing data'''
    proxy = self.getBusinessObjectProxy()
    usrobj = proxy.getObject('USROBJ')
    cmpobj = proxy.getObject('CMPOBJ')

    usrinfo = usrobj.retrieveUserInfoDict(mvcsession)
    diviinfo = cmpobj.getDivision(usrinfo['USRCONO'], usrinfo['USRDVNO'])

    mvcsession.entryDataset.Append()
    mvcsession.entryDataset.SetFieldValue('CMFACONO', diviinfo[0])
    mvcsession.entryDataset.SetFieldValue('CMFADVNO', diviinfo[2])
    mvcsession.entryDataset.SetFieldValue('CMFACONM', diviinfo[1])
    mvcsession.entryDataset.SetFieldValue('CMFADVNM', diviinfo[3])
    mvcsession.entryDataset.Post()
    return mvcsession

  def validateData(self, mvcsession):
    '''Validate date retrieved from user input before storing it into persistent storage'''
    fields = mvcsession.entryDataset.FieldsAsDict()
    validators.Assertion(messages={'assert': 'Circular reference on global facility'}).to_python(fields['CMFAGFNO'] != fields['CMFAFANO'])
    return mvcsession


