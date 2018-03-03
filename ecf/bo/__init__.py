import os, sys, imp, traceback
import itertools
from sets import Set

import ecflogger
import ecfpool
import tools

logger = ecflogger.Logger()

def registerClasses():
  logger = ecflogger.Logger()
  ad = tools.config['ecfserver.obj.path']
  _mod_list = []
  module_list = os.listdir(ad)
  pool = ecfpool.getOBJPool()

  for model in module_list:
    _pyfile = os.path.join(ad, model)
    _ext = model[-2:].lower()
    if _ext == 'py':
      _mod = model[:-3]
    elif _ext in ('yo', 'yc'):
      _mod = model[:-4]
    elif _ext == 'ss':
      _mod = model[:-9]
    if os.path.isfile(_pyfile) and (not(_mod in _mod_list)) and (_mod != "__init__") and (_mod.find('.') < 0):
      _mod_list.append(_mod)

  for _mod in _mod_list:
    fp, pathname, description = imp.find_module(_mod)
    try:
      try:
        imp.load_module('bo', fp, pathname, description)
        # logger.notifyChannel('init', ecflogger.LOG_INFO, 'OBJ:%s:registering business object class' % _mod)
        pool.instanciate(_mod)
      except Exception, e:
        print >>sys.stderr, 'ERROR on loading object %s, caught exception: %s' % (_mod, e)
        traceback.print_exc(file=sys.stderr)
    finally:
      if fp:
        fp.close()


