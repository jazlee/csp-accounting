import types
import inspect
import sys

__jited_count = 0
__jit_mode = 0
try:
  import _llvm
  if (_llvm.get_jit_control() == "whenhot"):
    __jited_count = -1
  __jit_mode = 1
  __jit_dict = {}
except:
  _llvm = None

try:
  if (__jit_mode == 0):
    import psyco
    __jit_mode = 2
except:
  psyco = None

def compile_llvm(func):
  """compile using unladen-swallow llvm"""
  if (_llvm != None) and \
     (hasattr(func, '__code__')) and \
     (func.__code__.__use_llvm__ == False):
    func.__code__.__use_llvm__ = True
    func.__code__.co_optimization = 2
    #
    # removing explicit compile, see reff:
    #    Explicitly compiling certain functions ahead
    #    of time, without allowing a chance to gather relevant runtime data
    #    about the types and values passing through your code, is guaranteed to
    #    result in below-expectations performance since our optimizations won't
    #    have that very-valuable data to take advantage of.
    #
    #    http://groups.google.com/group/unladen-swallow/msg/dd6135c1e988dd48
    #
    # _llvm.compile(func.__code__, 2)

def compile_psyco(func):
  """compile using psyco"""
  if (psyco != None): psyco.bind(func)

def compile_func_to_native(func):
  """Trying to compile to native"""
  if (__jit_mode in (1,2)):
    if (__jit_mode == 1):
      compile_llvm(func)
    else:
      compile_psyco(func)

def compile_obj_to_native(obj):
  """Trying to compile to native"""
  __jit_enabled = (__jit_mode in (1,2))
  if (__jit_enabled) and hasattr(obj, '__dict__'):
    fn_uncompiled = [fn_code for fn_name, fn_code in obj.__dict__.iteritems() \
                  if hasattr(fn_code, '__code__') ]
    for fnc in fn_uncompiled:
      compile_func_to_native(fnc)

def compile_module(module):
  for name in dir(module):
    obj = getattr(module, name)
    if inspect.isclass(obj):
      compile_obj_to_native(obj)
    elif inspect.ismethod(obj) or inspect.isfunction(obj):
      compile_func_to_native(obj)

def compile_package(pkg_name):
  """try to compile the package, it must be import before calling this
     input:
        pkg_name -> string
  """
  if (isinstance(pkg_name, types.StringType) != True):
    raise Exception('expecting string for input parameter')
  pkg_len = len(pkg_name)
  modlst = [module for modname, module in sys.modules.iteritems()
              if (modname[:pkg_len] == pkg_name)]
  for mod in modlst: compile_module(mod)

def nativemethod(func):
  """Native Method decorator, this will try to compile method decorate with this decorator
  example:
    class MyClass:
      @nativemethod
      def MyFunc(self, param):
        pass
  """
  def wrapper(self, *args, **kw):
    if (__jit_mode in (1,2)): compile_func_to_native(func)
    return func(self, *args, **kw)
  return wrapper

def nativeclass(cls):
  should_revisit = not (hasattr(cls, '__jit_compiled__') and (cls.__jit_compiled__ == True))
  if (_llvm != None) and (should_revisit):
    for key, element in cls.__dict__.iteritems():
      if hasattr(element,'__code__'):
        compile_func_to_native(element)
    setattr(cls, '__jit_compiled__', True)
  return cls

def nativefunc(func):
  def wrapper(*args, **kw):
    if (__jit_mode in (1,2)): compile_func_to_native(func)
    return func(*args, **kw)
  return wrapper

def profile_func(codeobj, max_threshold):
  if hasattr(codeobj, '__code__'):
    if (codeobj.__code__.co_hotness >= max_threshold) and \
       (codeobj.__code__.__use_llvm__ == False):
      return (codeobj, codeobj.__code__.co_hotness)
  return None

def profile_class(codeobj, funcdict, max_threshold):
  if hasattr(codeobj, '__dict__'):
    try:
      for funcname in codeobj.__dict__.keys():
        funcobj = codeobj.__dict__[funcname]
        func_tpl = profile_func(funcobj, max_threshold)
        if func_tpl != None:
          funcdict["%s.%s" % \
              (getattr(codeobj, '__name__', 'Unknown'),
               funcname)] = func_tpl
    except: pass

def run_profile(lastn = 200):
  global __jited_count, __jit_mode
  # This only works if:
  # 1. We use unladen-swallow engine
  # 2. Has not reach maximum limit of compiled code
  if (__jit_mode != 1) or (__jited_count > lastn) or (__jited_count < 0):
    return None
  max_threshold = _llvm.get_hotness_threshold()
  funcdict = {}
  for modname in sys.modules.keys():
    modobj = sys.modules[modname]
    for objname in dir(modobj):
      codeobj = getattr(modobj, objname)
      if inspect.isclass(codeobj):
        profile_class(codeobj, funcdict, max_threshold)
      elif inspect.ismethod(codeobj) or inspect.isfunction(codeobj):
        func_tpl =  profile_func(codeobj, max_threshold)
        if func_tpl != None:
          funcdict["%s.%s" % (modname, objname)] = func_tpl
  funclist = [(key, funcdict[key]) for key in funcdict.keys() \
      if (not __jit_dict.has_key(key))]
  sortedlist = sorted(funclist, key=lambda i: i[1][1],reverse=True)
  lastnlist = sortedlist[:lastn]
  for key, codeobj in lastnlist:
    __jit_dict[key] = codeobj[0]
    compile_func_to_native(codeobj)
  __jited_count = __jited_count + len(lastnlist)

compile_func_to_native(profile_func)
compile_func_to_native(profile_class)
compile_func_to_native(run_profile)
