
__all__ = ('CounterMeta')

class CounterMeta(type):

  counter = 0

  def __call__(self, *args, **kwargs):
    instance = type.__call__(self, *args, **kwargs)
    instance._counter = CounterMeta.counter
    CounterMeta.counter += 1
    return instance