#----------------------------------------------------------
# python imports
#----------------------------------------------------------
import os, signal, sys

import ecflogger
ecflogger.InitLogger()

import tools
rootscript_path = tools.config['ecfserver.root.script.path']
if rootscript_path is not None:
  sys.prefix = rootscript_path

if sys.platform=='win32':
  import mx.DateTime
  import time

  mx.DateTime.strptime = lambda x,y: mx.DateTime.mktime(time.strptime(x, y))

import site
from startup import *

