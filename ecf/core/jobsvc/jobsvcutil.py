import sys

__doc_all__ = []

MUTATORS = '__jobsvc_mutators__'

class JOBClassMutator(object):

  def __init__(self, handler):
    self.handler = handler

  def __call__(self, *args, **kwargs):
    class_locals = sys._getframe(1).f_locals
    mutators = class_locals.setdefault(MUTATORS, [])
    mutators.append((self, args, kwargs))

  def process(self, entity, *args, **kwargs):
    self.handler(entity, *args, **kwargs)


def process_mutators(mvcobj):
  mutators = getattr(mvcobj, MUTATORS, [])
  for mutator, args, kwargs in mutators:
    mutator.process(mvcobj, *args, **kwargs)
