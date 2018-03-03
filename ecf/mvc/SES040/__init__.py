"""
Table List
"""

__author__    = 'Jaimy Azle'
__version__   = '1.0'
__copyright__ = 'Copyright (c) 2009 Jaimy Azle'

import sys
from apisvc import *
from mvcsvc import *
from elixir import *
from validators import *

class SES040(MVCController):
  """
  Table List
  """

  _description = 'Persistent Model List'
  _active = True
  _supported_functions = (MVCFuncSelect, MVCFuncShow)

  EFDBTBNM    = MVCField(MVCTypeField + MVCTypeList, String(24), label = 'Model Name', enabled=False)
  EFDBTBDS    = MVCField(MVCTypeField + MVCTypeList, String(64), label = 'Description', enabled=False)

  def initView(self, mvcsession):
    mvcsession.extFunctions = (
      MVCExtFunction('Open field list', 'SES041', params = {'EFFDTBNM':'%f:EFDBTBNM', 'EFDBTBDS': '%f:EFDBTBDS'}),
      )
    mvcsession.selectFunction = MVCExtFunction('Open field list', 'SES041',
        params = {'EFDBTBNM':'%f:EFDBTBNM', 'EFDBTBDS': '%f:EFDBTDS'}
      )
    return mvcsession

  def openView(self, mvcsession):
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


    for entity in entities:
      _desc = ''
      if hasattr(entity, '__doc__') and (entity.__doc__):
        _desc = trim(entity.__doc__)

      mvcsession.listDataset.Append()
      mvcsession.listDataset.SetFieldValue('EFDBTBNM', entity._descriptor.tablename)
      mvcsession.listDataset.SetFieldValue('EFDBTBDS', _desc)
      mvcsession.listDataset.Post()
    return mvcsession

  def retrieveData(self, mvcsession):
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

    if mvcsession.execType in (MVCExecShow, MVCExecEdit):
      for entity in entities:
        if (entity._descriptor.tablename == mvcsession.listDataset.GetFieldValue('EFDBTBNM')):
          _desc = ''
          if hasattr(entity, '__doc__') and (entity.__doc__):
            _desc = trim(entity.__doc__)

          mvcsession.entryDataset.Append()
          mvcsession.entryDataset.SetFieldValue('EFDBTBNM', entity._descriptor.tablename)
          mvcsession.entryDataset.SetFieldValue('EFDBTBDS', _desc)
          mvcsession.entryDataset.Post()

    return mvcsession



