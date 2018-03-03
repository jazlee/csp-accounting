import logging

LOG_DEBUG='debug'
LOG_INFO='info'
LOG_WARNING='warn'
LOG_ERROR='error'
LOG_CRITICAL='critical'

class DefaultIOHandler:
  pyio = __import__('_ecfpyutils')
  softspace=0

  def write(self,message):
    self.pyio.logwrite(message)

  def readline(self, size=None):
    return self.pyio.logread(size)

  def flush(self):
    pass

  def seek(self, val):
    pass

def InitLogger():
  import os, sys

  # handler = logging.StreamHandler(sys.stdout)
  handler = logging.StreamHandler(DefaultIOHandler())

  # create a format for log messages and dates
  # formatter = logging.Formatter('%(asctime)s %(levelname)s:%(name)s:%(message)s', '%a, %d %b %Y %H:%M:%S')
  formatter = logging.Formatter('LOG:%(levelname)s:%(name)s:%(message)s')

  # tell the handler to use this format
  handler.setFormatter(formatter)

  # add the handler to the root logger
  logging.getLogger().addHandler(handler)
  logging.getLogger().setLevel(logging.INFO)

class Logger(object):
  def notifyChannel(self,name,level,msg):
    log = logging.getLogger(name)
    getattr(log,level)(msg)
