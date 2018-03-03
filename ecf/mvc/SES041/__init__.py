"""
Field List
"""

__author__    = 'Jaimy Azle'
__version__   = '1.0'
__copyright__ = 'Copyright (c) 2009 Jaimy Azle'

import sys
import fakeapi
from apisvc import *
from mvcsvc import *
from elixir import *
from sqlalchemy import types

class SES041(MVCController):
  """
  Field List
  """

  _description = 'Persistent Model Field List'
  _active = True
  _supported_functions = (MVCFuncShow,)

  EFDBTBNM    = MVCField(MVCTypeParam, String(24), label = 'Model Name', browseable=True, charcase=ecUpperCase, synchronized=True)
  EFDBTBDS    = MVCField(MVCTypeParam, String(64), label = 'Description', enabled=False)
  EFDBFLNM    = MVCField(MVCTypeField + MVCTypeList, String(24), label = 'Field Name', enabled=False)
  EFDBFLDS    = MVCField(MVCTypeField + MVCTypeList, String(64), label = 'Description', enabled=False)
  EFDBFLTP    = MVCField(MVCTypeField + MVCTypeList, String(16), label = 'Type', enabled=False)
  EFDBFLSZ    = MVCField(MVCTypeField + MVCTypeList, Integer, label = 'Size', enabled=False)
  EFDBFLPR    = MVCField(MVCTypeField + MVCTypeList, Integer, label = 'Precision', enabled=False)

  def lookupView(self, mvcsession, fieldName):
    ret = MVCLookupDef('','')
    if fieldName == 'EFDBTBNM':
      ret.svcname = 'SES040'
      ret.retfield = 'EFDBTBNM'
    return ret

  def synchronizeData(self, mvcsession, fieldName, fieldType):
    def trim(docstring):
      if not docstring:
          return ''
      # Convert tabs to spaces (following the normal Python rules)
      # and split into a list of lines:
      lines = docstring.expandtabs().splitlines()
      # Determine minimum indentation (first line doesn't count):
      indent = sys.maxint
      for line in lines[1:]:
          stripped = line.lstrip()
          if stripped:
              indent = min(indent, len(line) - len(stripped))
      # Remove indentation (first line is special):
      trimmed = [lines[0].strip()]
      if indent < sys.maxint:
          for line in lines[1:]:
              trimmed.append(line[indent:].rstrip())
      # Strip off trailing and leading blank lines:
      while trimmed and not trimmed[-1]:
          trimmed.pop()
      while trimmed and not trimmed[0]:
          trimmed.pop(0)
      # Return a single string:
      return '\n'.join(trimmed)

    def get_entity(etname):
      for entity in entities:
        if (entity._descriptor.tablename == etname):
          return entity
      return None

    if (fieldName == 'EFDBTBNM'):
      params = mvcsession.paramDataset.FieldsAsDict()
      entity = get_entity(params['EFDBTBNM'])
      _desc = ''
      if entity:
        _desc = trim(entity.__doc__)
      mvcsession.paramDataset.Edit()
      mvcsession.paramDataset.SetFieldValue('EFDBFLDS', _desc)
      mvcsession.paramDataset.Post()
    return mvcsession

  def openView(self, mvcsession):
    def get_entity(etname):
      for entity in entities:
        if (entity._descriptor.tablename == etname):
          return entity
      return None

    if not mvcsession.paramDataset.IsEmpty:
      params = mvcsession.paramDataset.FieldsAsDict()
      entity = get_entity(params['EFDBTBNM'])
      if entity:
        for field in entity._descriptor.builders:
          _type = types.to_instance(field.type)
          mvcsession.listDataset.Append()
          mvcsession.listDataset.SetFieldValue('EFDBFLNM', field.colname)
          mvcsession.listDataset.SetFieldValue('EFDBFLDS', field.tlabel)
          mvcsession.listDataset.SetFieldValue('EFDBFLTP', _type.get_ecf_type_ex())
          mvcsession.listDataset.SetFieldValue('EFDBFLSZ', getattr(field.type,'length', 0))
          mvcsession.listDataset.SetFieldValue('EFDBFLPR', getattr(field.type,'precision', 0))
          mvcsession.listDataset.Post()
    return mvcsession

  def retrieveData(self, mvcsession):
    if mvcsession.execType in (MVCExecShow,):
      fields = mvcsession.listDataset.FieldsAsDict()
      mvcsession.entryDataset.Append()
      mvcsession.entryDataset.SetFieldValue('EFDBFLNM', fields['EFDBFLNM'])
      mvcsession.entryDataset.SetFieldValue('EFDBFLDS', fields['EFDBFLDS'])
      mvcsession.entryDataset.SetFieldValue('EFDBFLTP', fields['EFDBFLTP'])
      mvcsession.entryDataset.SetFieldValue('EFDBFLSZ', fields['EFDBFLSZ'])
      mvcsession.entryDataset.SetFieldValue('EFDBFLPR', fields['EFDBFLPR'])
      mvcsession.entryDataset.Post()
    return mvcsession



