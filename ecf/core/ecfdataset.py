import sys, copy
import _ecfdatasetapi

EFDBOP_NONE   = 0
EFDBOP_APPEND = 1
EFDBOP_EDIT = 2
EFDBOP_DELETE = 3


class ECFNewDataset(object):
  """The New Dataset API"""

  def __init__(self):
    self.clear()

  def clear(self):
    self.curr_buffer = None
    self.curr_record = None
    self.rowset = list()
    self.lastop = 0

  def Open():
    pass

  def Close():
    self.clear()

  def Append():
    self.curr_buffer = dict()
    self.lastop = EFDBOP_APPEND

  def Edit():
    self.curr_buffer = copy.deepcopy(self.curr_record)
    self.lastop = EFDBOP_EDIT

  def Post():
    if self.lastop == EFDBOP_APPEND:
      self.curr_record = copy.deepcopy(self.curr_buffer)
      self.rowset.append(self.curr_record)
      self.lastop = EFDBOP_NONE
    elif self.lastop == EFDBOP_EDIT:
      for key in self.curr_buffer.keys():
        self.curr_buffer[key] = copy.deepcopy(self.curr_buffer[key])
      self.lastop = EFDBOP_NONE
    else:
      raise Exception("unknown operation")

  def Cancel(self):
    if (self.lastop != EFDBOP_NONE):
      self.curr_buffer = None
      self.lastop = EFDBOP_NONE

  def Delete(self):
    if self.curr_record in self.rowset:
      self.rowset.remove(self.curr_record)
      self.curr_record = None
      if len(self.rowset) > 0:
        self.curr_record = self.rowset[0]

  def SetFieldValue(self, field, value):
    """Set the value into field"""
    self.curr_buffer[field] = value

  def SetFieldValues(self, dictvalues):
    """Set several values into fields, the value sent must be stored in dict datatype
       example:
          adict = {'CMCPCONO':'DEF', 'CMCPCONM':'Default Company'}
          SetFieldValues(adict)
    """
    if isinstance(dictvalues, dict):
      for fieldName, value in dictvalues.iteritems():
        self.SetFieldValue(fieldName, value)
    else:
      raise Exception('parameter sent is not a dict datatype')

  def GetFieldValue(self, field):
    """Get the value of the field"""
    return None if self.curr_buffer.has_key(field) != True \
      else curr_buffer[field]

  def FieldsAsDict(self):
    """Transform a recordset into Dictionary"""
    return copy.deepcopy(self.curr_record)

  def FieldsAsDictExt(self):
    """Transform a recordset into Dictionary"""
    return _ecfdatasetapi.dataset_getdictext(self.dataset_ptr)

  @property
  def RecordCount(self):
    """Get record count"""
    return len(self.rowset)

  @property
  def IsEmpty(self):
    """Check if the record is empty"""
    return (len(self.rowset) == 0)

  def IsActive(self):
    return True

class ECFDataset(object):
  """Delphi TDataset wrapper class to hold data sent and received by client"""

  def __init__(self, dsPtr):
    """Construct the dataset object"""
    self.dataset_ptr = dsPtr

  def Open(self):
    """Open the dataset, by default the dataset has been opened by server"""
    _ecfdatasetapi.dataset_open(self.dataset_ptr)

  def Close(self):
    """Close the dataset, there is almost no need to close the dataset as this will
       be done by the server"""
    _ecfdatasetapi.dataset_close(self.dataset_ptr)

  def Append(self):
    """Initialize the dataset for record appending"""
    _ecfdatasetapi.dataset_append(self.dataset_ptr)

  def Edit(self):
    """Initialize the dataset for record editing"""
    _ecfdatasetapi.dataset_edit(self.dataset_ptr)

  def Post(self):
    """Post the record in buffer into saved state"""
    _ecfdatasetapi.dataset_post(self.dataset_ptr)

  def Cancel(self):
    """Cancel any previously changed state"""
    _ecfdatasetapi.dataset_cancel(self.dataset_ptr)

  def SetFieldValue(self, field, value):
    """Set the value into field"""
    _ecfdatasetapi.dataset_setvalue(self.dataset_ptr, field, value)

  def SetFieldValues(self, dictvalues):
    """Set several values into fields, the value sent must be stored in dict datatype
       example:
          adict = {'CMCPCONO':'DEF', 'CMCPCONM':'Default Company'}
          SetFieldValues(adict)
    """
    if isinstance(dictvalues, dict):
      for fieldName, value in dictvalues.iteritems():
        _ecfdatasetapi.dataset_setvalue(self.dataset_ptr, fieldName, value)
    else:
      raise Exception('parameter sent is not a dict datatype')

  def GetFieldValue(self, field):
    """Get the value of the field"""
    return _ecfdatasetapi.dataset_getvalue(self.dataset_ptr, field)

  def FieldsAsDict(self):
    """Transform a recordset into Dictionary"""
    return _ecfdatasetapi.dataset_getdict(self.dataset_ptr)

  def FieldsAsDictExt(self):
    """Transform a recordset into Dictionary"""
    return _ecfdatasetapi.dataset_getdictext(self.dataset_ptr)

  def _getrecordcount(self):
    """Get record count"""
    return _ecfdatasetapi.dataset_getrecordcount(self.dataset_ptr)

  RecordCount = property(_getrecordcount)

  def _getisempty(self):
    """Check if the record is empty"""
    return _ecfdatasetapi.dataset_isempty(self.dataset_ptr)

  IsEmpty = property(_getisempty)

  def _getisactive(self):
    return _ecfdatasetapi.dataset_isactive(self.dataset_ptr)

  IsActive = property(_getisactive)

  def CopyFromORM(self, srcfields, dstfields, obj):
    """Copy values from ORM rowset into dataset"""
    _ecfdatasetapi.dataset_copyfromorm(self.dataset_ptr, srcfields, dstfields, obj)

  def CopyFromORMList(self, srcfields, dstfields, objs):
    """Copy all resultset values from ORM into dataset"""
    _ecfdatasetapi.dataset_copyfromormlist(self.dataset_ptr, srcfields, dstfields, objs)

  def CopyIntoORM(self, srcfields, dstfields, obj):
    """Copy rowset values from dataset into ORM instance"""
    _ecfdatasetapi.dataset_copyintoorm(self.dataset_ptr, srcfields, dstfields, obj)

  def CopyFromDictIntoORM(self, dictvalues, obj):
    if isinstance(dictvalues, dict):
      for fieldname in dictvalues.keys():
        if hasattr(obj, fieldname):
          setattr(obj, fieldname, dictvalues[fieldname])
    else:
      raise Exception('parameter sent is not a dict datatype')



def createECFDataset(dsPtr):
  return ECFDataset(dsPtr)

def getECFDataset(dsPtr):
  return createECFDataset(dsPtr)
