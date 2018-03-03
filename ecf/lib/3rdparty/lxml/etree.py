def __bootstrap__():
   global __bootstrap__, __file__
   import sys, imp
   __file__ = '_etree.pyd'
   del __bootstrap__
   imp.load_dynamic(__name__,__file__)
__bootstrap__()