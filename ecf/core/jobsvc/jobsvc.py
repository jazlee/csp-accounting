import sys
import copy
import string
import ecfexceptions
from jobsvcutil import JOBClassMutator, process_mutators
from jitutil import *
import datetime as dt
from elixir import session
from procsvc import getBOProxy

_moduleClassList = {}
_classPool = {}
_services = {}
_groups = {}

jobs = list()

JOBStatusUnassigned = 10
JOBStatusBusy = 20
JOBStatusCompleted = 30
JOBStatusError = 99

options_defaults = dict(
  inheritance='single',
  polymorphic=False,
  jobname=None,
  allowcoloverride=False
  )

class JOBService(object):

  def __init__(self, name):
    _services[name] = self
    self._name = name
    self._methods = {}
    self._exportedMethods = None

  def joinGroup(self, name):
    if not name in _groups:
      _groups[name] = {}
    _groups[name][self._name] = self

  def exportMethod(self, proc):
    if callable(proc):
      self._methods[proc.__name__] = proc

  def abortResponse(self, description, origin, details):
    raise ecfexceptions.ECFJOBServiceNotAvailable("%s -- %s: %s"%(origin,description,details))

class JOBLocalService(JOBService):

  def __init__(self, name):
    self._name = name
    svc = _services[name]
    for proc in svc._methods:
      setattr(self, proc, svc._methods[proc])

class JOBPool(JOBService):

  def __init__(self):
    self._objPool = {}
    super(JOBPool, self).__init__('__JOBPROXY__')
    self.joinGroup('__JOBSVC__')
    self.exportMethod(self._exportedMethods)
    self.exportMethod(self.getSession)
    self.exportMethod(self.executeJob)

  def add(self, name, objInstance):
    if self._objPool.has_key(name):
      del self._objPool[name]
    self._objPool[name] = objInstance

  def get(self, name):
    return self._objPool.get(name, None)

  def instanciate(self, module):
    res = []
    classList = _moduleClassList.get(module, [])
    for klass in classList:
      res.append(klass.createInstance(self, module))
    return res

  def getObject(self, obj):
    object = self._objPool.get(obj)
    if not object:
      self.abortResponse('Object Error', 'warning',
        'JOB Object %s does not exist' % str(obj))
    else:
      return object
    return None

  def updateJobStatus(self, jobID, status, msg):
    from tbl import EFJBLS
    from elixir import session
    session.close()
    obj = EFJBLS.query.filter_by(JBLSIDNM = jobID).first()

    pgmName = None
    if obj:
      pgmName = obj.JBLSPRPG
      now = dt.datetime.now()
      if obj.JBLSPRDT is None:
        obj.JBLSPRDT = now.date().tointeger()
      if obj.JBLSPRTM is None:
        obj.JBLSPRTM = now.time().tointeger()
      obj.JBLSUPDT = now.date().tointeger()
      obj.JBLSUPTM = now.time().tointeger()
      obj.JBLSPRST = status
      if msg:
        msg = msg[:64]
      obj.JBLSPRMS = msg
      if not session.transaction_started():
        session.begin()
      try:
        session.update(obj)
        session.commit()
      except:
        session.rollback()
        raise
    return pgmName

  def getSession(self):
    # object = self.getObject(obj)
    # return object.__getsession__()
    return JOBSession()

  def executeJob(self, jobsession):
    # object = self.getObject(obj)
    # return object.executeJob(*args)
    try:
      pgmName = self.updateJobStatus(jobsession.jobID, 10, None)
      try:
        if not pgmName:
          raise Exception('No JOB Processor defined for jobID=%s' % jobsession.jobID)
        pgmObj = self.getObject(pgmName)
        # try to compile first before doing job execution
        compile_obj_to_native(pgmObj)
        pgmObj.executeJob(jobsession)
        self.updateJobStatus(jobsession.jobID, 100, None)
      except Exception, e:
        self.updateJobStatus(jobsession.jobID, 99, e.message)
        raise
    finally:
      session.close()



class JOBSession(object):

  def __init__(self):
    self.cookies = {}
    self.jobID=None
    self.processingJob=None
    self.processStatus=JOBStatusUnassigned

  def getCookies(self):
    cookies = [(key, value) for key, value in self.cookies.iteritems()]
    tpcookies = sorted(cookies, key=lambda i: i[0])
    return tuple(tpcookies)

  def setCookies(self, cookies):
    for key, value in cookies:
      self.cookies[key] = value

class JOBDescriptor(object):

  def __init__(self, job, name):
    self.job = job
    module = str(job)[6:]
    module = module[:len(module)-1]
    module = module.split('.')[0][2:]
    self.module = module
    self.parent = None
    self.children = []
    for base in job.__bases__:
      if issubclass(base, JOBEngine) and base is not JOBEngine:
        if self.parent:
          raise Exception('%s job inherits from several jobss,'
            ' and this is not supported.'
            % self.job.__name__)
        else:
          self.parent = base
          self.parent._descriptor.children.append(job)
    self.properties = dict()
    for option in options_defaults.keys():
      setattr(self, option, options_defaults[option])
    self.collection = getattr(self.module, '__job_collection__',
                                  jobs)
    _moduleClassList.setdefault(self.module, []).append(job)
    _classPool[name] = job

  def add_property(self, name, property, check_duplicate=True):
    if check_duplicate and name in self.properties:
        raise Exception("property '%s' already exist in '%s' ! " %
                        (name, self.job.__name__))
    self.properties[name] = property

  def setup_options(self):
    '''
    Setup any values that might depend on using_options. For example, the
    job.name.
    '''
    if self.collection is not None:
      self.collection.append(self.job)

    job = self.job
    if self.inheritance == 'concrete' and self.polymorphic:
      raise NotImplementedError("Polymorphic concrete inheritance is "
                                  "not yet implemented.")

    if self.parent:
      if self.inheritance == 'single':
        self.jobname = self.parent._descriptor.jobname

    if not self.jobname:
      self.jobname = job.__name__.upper()
    elif callable(self.jobname):
      self.jobname = self.jobname(job)

def _is_job(class_):
  return isinstance(class_, JOBMeta)

class JOBMeta(type):

  _jobs = {}

  def __init__(cls, name, bases, dict_):
    # only process subclasses of Form, not Form itself
    if bases[0] is object:
      return

    # build a dict of entities for each frame where there are entities
    # defined
    caller_frame = sys._getframe(1)
    cid = cls._caller = id(caller_frame)
    caller_jobs = JOBMeta._jobs.setdefault(cid, {})
    caller_jobs[name] = cls

    # Append all jobs which are currently visible by the job. This
    # will find more entities only if some of them where imported from
    # another module.
    for job in [e for e in caller_frame.f_locals.values()
                     if _is_job(e)]:
        caller_jobs[job.__name__] = job

    # create the job descriptor
    desc = cls._descriptor = JOBDescriptor(cls, name)

    # process mutators
    process_mutators(cls)

    # setup misc options here (like jobname etc.)
    desc.setup_options()

  def __call__(cls, *args, **kwargs):
    return type.__call__(cls, *args, **kwargs)

class JOBEngine(object):

  __metaclass__ = JOBMeta

  def __init__(self, pool):
    pool.add(self._descriptor.jobname, self)
    self.pool = pool

  def __getsession__(self):
    return JOBSession()

  def createInstance(cls, pool, module):
    obj = object.__new__(cls)
    obj.__init__(pool)
    return obj

  createInstance = classmethod(createInstance)

  def getBusinessObjectProxy(self):
    return getBOProxy()

  def executeJob(self, jobsession):
    pass

def createJOBLocalService(name):
  return JOBLocalService(name)

def getJOBLocalService(name):
  return createJOBLocalService(name)

