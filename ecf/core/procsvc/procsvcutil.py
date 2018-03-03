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

import sys

__doc_all__ = []

MUTATORS = '__proc_mutators__'

class BusinessObjectClassMutator(object):

  def __init__(self, handler):
    self.handler = handler

  def __call__(self, *args, **kwargs):
    class_locals = sys._getframe(1).f_locals
    mutators = class_locals.setdefault(MUTATORS, [])
    mutators.append((self, args, kwargs))

  def process(self, entity, *args, **kwargs):
    self.handler(entity, *args, **kwargs)


def process_mutators(bobj):
  mutators = getattr(bobj, MUTATORS, [])
  for mutator, args, kwargs in mutators:
    mutator.process(bobj, *args, **kwargs)
