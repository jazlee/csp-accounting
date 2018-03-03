import os, sys, imp, traceback
import itertools
from sets import Set

import ecflogger
import ecfpool
import tools

logger = ecflogger.Logger()

opj = os.path.join
ad = tools.config['ecfserver.modules.path']
sys.path.insert(1,ad)

def registerClasses():
  _mod_list = []
  module_list = os.listdir(ad)
  pool = ecfpool.getMVCPool()

  for mod in module_list:
    _pyfile = opj(ad, mod, '__init__.py')
    if os.path.isfile(_pyfile):
      _mod_list.append(mod)
    else:
      _pyfile = opj(ad, mod, '__init__.pyo')
      if os.path.isfile(_pyfile):
        _mod_list.append(mod)
      else:
        _pyfile = opj(ad, mod, '__init__$py.class')
        if os.path.isfile(_pyfile):
          _mod_list.append(mod)

  for mod in _mod_list:
    # logger.notifyChannel('init', ecflogger.LOG_INFO, 'MVC:%s:registering mvc controller class' % mod)
    # sys.stdout.flush()
    try:
      imp.load_module(mod, *imp.find_module(mod))
      pool.instanciate(mod)
    except Exception, e:
      print >>sys.stderr, 'ERROR on loading MVC module %s, caught exception: %s' % (mod, e)
      traceback.print_exc(file=sys.stderr)


