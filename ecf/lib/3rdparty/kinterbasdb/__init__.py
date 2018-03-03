# KInterbasDB Python Package - Python Wrapper for Core
#
# Version 3.2
#
# The following contributors hold Copyright (C) over their respective
# portions of code (see license.txt for details):
#
# [Original Author (maintained through version 2.0-0.3.1):]
#   1998-2001 [alex]  Alexander Kuznetsov   <alexan@users.sourceforge.net>
# [Maintainers (after version 2.0-0.3.1):]
#   2001-2002 [maz]   Marek Isalski         <kinterbasdb@maz.nu>
#   2002-2006 [dsr]   David Rushby          <woodsplitter@rocketmail.com>
# [Contributors:]
#   2001      [eac]   Evgeny A. Cherkashin  <eugeneai@icc.ru>
#   2001-2002 [janez] Janez Jere            <janez.jere@void.si>

#   The doc strings throughout this module explain what API *guarantees*
# kinterbasdb makes.
#   Notably, the fact that users can only rely on the return values of certain
# functions/methods to be sequences or mappings, not instances of a specific
# class.  This policy is still compliant with the DB API spec, and is more
# future-proof than implying that all of the classes defined herein can be
# relied upon not to change.  Module members whose names begin with an
# underscore cannot be expected to have stable interfaces.

__version__ = (3, 2, 0, 'final', 0)
__timestamp__ = '2008.04.16.16.14.27.UTC'

import os, struct, sys

if sys.platform.lower().startswith('win'):
    import os.path

    # Better out-of-box support for embedded DB engine on Windows:  if the
    # client library is detected in the same directory as kinterbasdb, or in
    # the 'embedded' subdirectory of kinterbasdb's directory, or in the same
    # directory as the Python executable, give that precedence over the
    # location listed in the registry.
    #
    # Client programmers who happen to read this should note that the embedded
    # engine malfunctions in various ways unless it's located in the same
    # directory as the actual executable (python.exe).
    _clientLibDir = None
    _kinterbasdbDir = os.path.dirname(os.path.abspath(__file__))
    for _clientLibName in (
        'firebird.dll', # Vulcan
        'fbclient.dll', # FB 1.5, 2.x
      ):
        for _location in (
            os.path.join(os.getcwd(), _clientLibName),
            os.path.join(_kinterbasdbDir, _clientLibName),
            os.path.join(os.path.join(_kinterbasdbDir, 'embedded'),
                _clientLibName
              ),
            os.path.join(os.path.dirname(sys.executable), _clientLibName),
          ):
            if os.path.isfile(_location):
                _clientLibDir = os.path.dirname(_location)
                break

        if _clientLibDir:
            break

    if _clientLibDir:
        os.environ['PATH'] = _clientLibDir + os.pathsep + os.environ['PATH']
        # At least with FB 1.5.2, the FIREBIRD environment variable must also
        # be set in order for all features to work properly.
        os.environ['FIREBIRD'] = _clientLibDir
    else:
        # FB 1.5 RC7 and later, when installed via the packaged installer or
        # the "instreg.exe" command-line tool, record their installation dir in
        # the registry.  If no client library was detected earlier, we'll add
        # the "bin" subdirectory of the directory from the registry to the
        # *end* of the PATH, so it'll be used as a last resort.
        import _winreg

        _reg = _winreg.ConnectRegistry(None, _winreg.HKEY_LOCAL_MACHINE)
        try:
            try:
                _dbInstPathsKey = _winreg.OpenKey(
                    _reg, r'SOFTWARE\Firebird Project\Firebird Server'
                           '\Instances'
                  )
                try:
                    _instPath = _winreg.QueryValueEx(
                        _dbInstPathsKey, 'DefaultInstance'
                      )[0]
                finally:
                    _dbInstPathsKey.Close()
                    del _dbInstPathsKey
            except WindowsError:
                # Versions of IB/FB prior to FB 1.5 RC7 don't have this _reg
                # entry, but they install the client library into a system
                # library directory, so there's no problem.
                pass
            else:
                os.environ['PATH'] += os.pathsep + os.path.join(
                    _instPath, 'bin'
                  )
                del _instPath
        finally:
            _reg.Close()

        del _winreg, _reg

    del _clientLibDir, _kinterbasdbDir, _clientLibName, _location

# The underlying C module:
import _kinterbasdb as _k

# Import database API constants into the namespace of this module as Python
# objects:
_k.init_kidb_basic_header_constants(globals())

# Export utility members:
FB_API_VER = _k.FB_API_VER

portable_int = _k.portable_int
raw_timestamp_to_tuple = _k.raw_timestamp_to_tuple

DEFAULT_CONCURRENCY_LEVEL = _k.DEFAULT_CONCURRENCY_LEVEL
get_concurrency_level = _k.concurrency_level_get

# Initialize the k_exceptions so that other Python modules in kinterbasdb can
# have access to kinterbasdb's exceptions without a circular import.
import k_exceptions

Warning               = k_exceptions.Warning            = _k.Warning
Error                 = k_exceptions.Error              = _k.Error
InterfaceError        = k_exceptions.InterfaceError     = _k.InterfaceError
DatabaseError         = k_exceptions.DatabaseError      = _k.DatabaseError
DataError             = k_exceptions.DataError          = _k.DataError
OperationalError      = k_exceptions.OperationalError   = _k.OperationalError
IntegrityError        = k_exceptions.IntegrityError     = _k.IntegrityError
InternalError         = k_exceptions.InternalError      = _k.InternalError

ProgrammingError      = k_exceptions.ProgrammingError   = _k.ProgrammingError
TransactionConflict          = k_exceptions.TransactionConflict       = _k.TransactionConflict

NotSupportedError     = k_exceptions.NotSupportedError  = _k.NotSupportedError

_EVENT_HANDLING_SUPPORTED = hasattr(_k, 'ConduitWasClosed')
if _EVENT_HANDLING_SUPPORTED:
    ConduitWasClosed  = k_exceptions.ConduitWasClosed   = _k.ConduitWasClosed

_CONNECTION_TIMEOUT_SUPPORTED = hasattr(_k, 'ConnectionTimedOut')
if _CONNECTION_TIMEOUT_SUPPORTED:
    ConnectionTimedOut = k_exceptions.ConnectionTimedOut = \
      _k.ConnectionTimedOut
    import _connection_timeout

_ALL_EXCEPTION_CLASSES = [
    Warning,
    Error,
    InterfaceError,
    DatabaseError,
    DataError,
    OperationalError,
    IntegrityError,
    InternalError,
    ProgrammingError,
    NotSupportedError,
  ]

if _EVENT_HANDLING_SUPPORTED:
    _ALL_EXCEPTION_CLASSES.append(ConduitWasClosed)

if _CONNECTION_TIMEOUT_SUPPORTED:
    _ALL_EXCEPTION_CLASSES.append(ConnectionTimedOut)

_ALL_EXCEPTION_CLASSES = tuple(_ALL_EXCEPTION_CLASSES)

##########################################
##     PUBLIC CONSTANTS: BEGIN          ##
##########################################

# Note:  Numerous database API constants were imported into the global
# namespace of this module by an earlier call to
# _k.init_kidb_basic_header_constants.  See _kinterbasdb_constants.c for more
# info.

apilevel = '2.0'
threadsafety = 1
paramstyle = 'qmark'

# Named positional constants to be used as indices into the description
# attribute of a cursor (these positions are defined by the DB API spec).
# For example:
#   nameOfFirstField = cursor.description[0][kinterbasdb.DESCRIPTION_NAME]

DESCRIPTION_NAME            = 0
DESCRIPTION_TYPE_CODE       = 1
DESCRIPTION_DISPLAY_SIZE    = 2
DESCRIPTION_INTERNAL_SIZE   = 3
DESCRIPTION_PRECISION       = 4
DESCRIPTION_SCALE           = 5
DESCRIPTION_NULL_OK         = 6

# Default transaction parameter buffer:
default_tpb = (
      # isc_tpb_version3 is a *purely* infrastructural value.  kinterbasdb will
      # gracefully handle user-specified TPBs that don't start with
      # isc_tpb_version3 (as well as those that do start with it).
      isc_tpb_version3

    + isc_tpb_write                                 # Access mode
    + isc_tpb_read_committed + isc_tpb_rec_version  # Isolation level
    + isc_tpb_wait                                  # Lock resolution strategy
    + isc_tpb_shared                                # Table reservation
                                                    # access method
  )

from _request_buffer_builder import RequestBufferBuilder as _RequestBufferBuilder
_request_buffer_builder.portable_int = portable_int

##########################################
##     PUBLIC CONSTANTS: END            ##
##########################################


###################################################
## DYNAMIC TYPE TRANSLATION CONFIGURATION: BEGIN ##
###################################################
# Added deferred loading of dynamic type converters to facilitate the
# elimination of all dependency on the mx package.  The implementation is quite
# ugly due to backward compatibility constraints.

BASELINE_TYPE_TRANSLATION_FACILITIES = (
    # Date and time translator names:
    'date_conv_in', 'date_conv_out',
    'time_conv_in', 'time_conv_out',
    'timestamp_conv_in', 'timestamp_conv_out',

    # Fixed point translator names:
    'fixed_conv_in_imprecise', 'fixed_conv_in_precise',
    'fixed_conv_out_imprecise', 'fixed_conv_out_precise',

    # Optional unicode converters:
    'OPT:unicode_conv_in', 'OPT:unicode_conv_out',

    # DB API 2.0 standard date and time type constructors:
    'Date', 'Time', 'Timestamp',
    'DateFromTicks', 'TimeFromTicks', 'TimestampFromTicks',
  )

# The next three will be modified by the init function as appropriate:
_MINIMAL_TYPE_TRANS_TYPES = ('DATE', 'TIME', 'TIMESTAMP', 'FIXED',)
_NORMAL_TYPE_TRANS_IN = None
_NORMAL_TYPE_TRANS_OUT = None


initialized = False
def init(type_conv=1, concurrency_level=_k.DEFAULT_CONCURRENCY_LEVEL):
    global initialized, _MINIMAL_TYPE_TRANS_TYPES, \
           _NORMAL_TYPE_TRANS_IN, _NORMAL_TYPE_TRANS_OUT

    if initialized:
        raise ProgrammingError('Cannot initialize module more than once.')

    if _k.DEFAULT_CONCURRENCY_LEVEL == 0:
        if concurrency_level != 0:
            raise ProgrammingError('Support for concurrency was disabled at'
                ' compile time, so only Level 0 is available.'
              )
        # Since only Level 0 is available and it's already active, there's no
        # need to do anything.
    else:
        if concurrency_level not in (1,2):
            raise ProgrammingError('Only Levels 1 and 2 are accessible at'
                ' runtime; Level 0 can only be activated at compile time.'
              )
        _k.concurrency_level_set(concurrency_level)

    _k.provide_refs_to_python_entities(
        _RowMapping,
        _make_output_translator_return_type_dict_from_trans_dict,
        _look_up_array_descriptor,
        _look_up_array_subtype,
        _Cursor_execute_exception_type_filter,
      )

    globalz = globals()
    if not isinstance(type_conv, int):
        typeConvModule = type_conv
    else:
        typeConvOptions = {
              0: 'typeconv_naked',
              1: 'typeconv_backcompat', # the default
            100: 'typeconv_23plus',
            199: 'typeconv_23plus_lowmem',
            200: 'typeconv_24plus',     # considered the "ideal" as of KIDB 3.2
          }
        chosenTypeConvModuleName = typeConvOptions[type_conv]
        typeConvModule = __import__('kinterbasdb.' + chosenTypeConvModuleName,
            globalz, locals(), (chosenTypeConvModuleName,)
          )
        if type_conv > 1:
            _MINIMAL_TYPE_TRANS_TYPES = \
              _MINIMAL_TYPE_TRANS_TYPES + ('TEXT_UNICODE',)

    for name in BASELINE_TYPE_TRANSLATION_FACILITIES:
        if not name.startswith('OPT:'):
            typeConvModuleMember = getattr(typeConvModule, name)
        else:
            # Members whose entries in BASELINE_TYPE_TRANSLATION_FACILITIES
            # begin with 'OPT:' are not required.
            name = name[4:]
            try:
                typeConvModuleMember = getattr(typeConvModule, name)
            except AttributeError:
                continue

        globalz[name] = typeConvModuleMember

    # Modify the initial, empty version of the DB API type singleton DATETIME,
    # transforming it into a fully functional version.
    # The fact that the object is *modifed* rather than replaced is crucial to
    # the preservation of compatibility with the 'from kinterbasdb import *'
    # form of importation.
    DATETIME.values = (
        # Date, Time, and Timestamp refer to functions just loaded from the
        # typeConvModule in the loop above.
        type(Date(2003,12,31)),
        type(Time(23,59,59)),
        type(Timestamp(2003,12,31,23,59,59))
      )

    _NORMAL_TYPE_TRANS_IN = {
        'DATE': date_conv_in,
        'TIME': time_conv_in,
        'TIMESTAMP': timestamp_conv_in,
        'FIXED': fixed_conv_in_imprecise,
      }
    _NORMAL_TYPE_TRANS_OUT = {
        'DATE': date_conv_out,
        'TIME': time_conv_out,
        'TIMESTAMP': timestamp_conv_out,
        'FIXED': fixed_conv_out_imprecise,
      }
    if type_conv > 1:
        _NORMAL_TYPE_TRANS_IN['TEXT_UNICODE'] = unicode_conv_in
        _NORMAL_TYPE_TRANS_OUT['TEXT_UNICODE'] = unicode_conv_out

    initialized = True

def _ensureInitialized():
    if not initialized:
        init()

# The following constructors will be replaced when kinterbasdb.init is called,
# whether implicitly or explicitly.  If one of the constructors is called
# before kinterbasdb.init, it will trigger its own replacement by calling
# _ensureInitialized.
def Date(year, month, day):
    _ensureInitialized()
    return Date(year, month, day)

def Time(hour, minute, second):
    _ensureInitialized()
    return Time(hour, minute, second)

def Timestamp(year, month, day, hour, minute, second):
    _ensureInitialized()
    return Timestamp(year, month, day, hour, minute, second)

def DateFromTicks(ticks):
    _ensureInitialized()
    return DateFromTicks(ticks)

def TimeFromTicks(ticks):
    _ensureInitialized()
    return TimeFromTicks(ticks)

def TimestampFromTicks(ticks):
    _ensureInitialized()
    return TimestampFromTicks(ticks)


###################################################
## DYNAMIC TYPE TRANSLATION CONFIGURATION: END   ##
###################################################


############################################
## PUBLIC DB-API TYPE CONSTRUCTORS: BEGIN ##
############################################

# All date/time constructors are loaded dynamically by the init function.

# Changed from buffer to str in 3.1, with the possible addition of a lazy BLOB
# reader at some point in the future:
Binary = str


# DBAPITypeObject implementation is the DB API's suggested implementation.
class DBAPITypeObject: # Purposely remains a "classic class".
    def __init__(self, *values):
        self.values = values
    def __cmp__(self, other):
        if other in self.values:
            return 0
        if other < self.values:
            return 1
        else:
            return -1


STRING = DBAPITypeObject(str, unicode)

BINARY = DBAPITypeObject(str, buffer)

NUMBER = DBAPITypeObject(int, long, float)

# DATETIME is loaded in a deferred manner (in the init function); this initial
# version remains empty only temporarily.
DATETIME = DBAPITypeObject()

ROWID = DBAPITypeObject()

############################################
## PUBLIC DB-API TYPE CONSTRUCTORS: END   ##
############################################


##########################################
##     PUBLIC FUNCTIONS: BEGIN          ##
##########################################

def connect(*args, **keywords_args):
    """
      Minimal arguments: keyword args $dsn, $user, and $password.
      Establishes a kinterbasdb.Connection to a database.  See the docstring
    of kinterbasdb.Connection for details.
    """
    return Connection(*args, **keywords_args)


def create_database(*args):
    """
      Creates a new database with the supplied "CREATE DATABASE" statement.
      Returns an active kinterbasdb.Connection to the newly created database.

    Parameters:
    $sql: string containing the CREATE DATABASE statement.  Note that you may
       need to specify a username and password as part of this statement (see
       the Firebird SQL Reference for syntax).
    $dialect: (optional) the SQL dialect under which to execute the statement
    """
    _ensureInitialized()

    # For a more general-purpose immediate execution facility (the non-"CREATE
    # DATABASE" variant of isc_dsql_execute_immediate, for those who care), see
    # Connection.execute_immediate.

    C_con = _k.create_database(*args)
    return Connection(_CConnection=C_con)


def raw_byte_to_int(raw_byte):
    """
      Convert the byte in the single-character Python string $raw_byte into a
    Python integer.  This function is essentially equivalent to the built-in
    function ord, but is different in intent (see the database_info method).
    """
    _ensureInitialized()

    if len(raw_byte) != 1:
        raise ValueError('raw_byte must be exactly one byte, not %d bytes.'
            % len(raw_byte)
          )
    return struct.unpack('b', raw_byte)[0]


##########################################
##     PUBLIC FUNCTIONS: END            ##
##########################################


##########################################
##     PUBLIC CLASSES: BEGIN            ##
##########################################

# BlobReader, PreparedStatement and Cursor can't be instantiated from Python,
# but are exposed here to support isinstance(o, kinterbasdb.Class) and the
# like.
BlobReader = _k.BlobReader
PreparedStatement = _k.PreparedStatement
Cursor = _k.Cursor

if _EVENT_HANDLING_SUPPORTED:
    EventConduit = _k.EventConduit

class Connection(object):
    """
      Represents a connection between the database client (the Python process)
    and the database server.

      The basic behavior of this class is documented by the Python DB API
    Specification 2.0; this docstring covers only some extensions.  Also see
    the KInterbasDB Usage Guide (docs/usage.html).

    Attributes:
    $dialect (read-only):
       The Interbase SQL dialect of the connection.  One of:
         1 for Interbase < 6.0
         2 for "migration mode"
         3 for Interbase >= 6.0 and Firebird (the default)

    $precision_mode (read/write): (DEPRECATED)
         precision_mode is deprecated in favor of dynamic type translation
       (see the [set|get]_type_trans_[in|out] methods, and the Usage Guide).
       ---
         precision_mode 0 (the default) represents database fixed point values
       (NUMERIC/DECIMAL fields) as Python floats, potentially losing precision.
         precision_mode 1 represents database fixed point values as scaled
       Python integers, preserving precision.
         For more information, see the KInterbasDB Usage Guide.

    $server_version (read-only):
         The version string of the database server to which this connection
       is connected.

    $default_tpb (read/write):
         The transaction parameter buffer (TPB) that will be used by default
       for new transactions opened in the context of this connection.
         For more information, see the KInterbasDB Usage Guide.
    """

    def __init__(self, *args, **keywords_args):
        # self._C_con is the instance of ConnectionType that represents this
        # connection in the underlying C module _k.

        _ensureInitialized()

        # Optional DB API Extension: Make the module's exception classes
        # available as connection attributes to ease cross-module portability:
        for exc_class in _ALL_EXCEPTION_CLASSES:
            setattr(self, exc_class.__name__, exc_class)

        # Inherit the module-level default TPB.
        self._default_tpb = default_tpb

        # Allow other code WITHIN THIS MODULE to obtain an instance of
        # ConnectionType some other way and provide it to us instead of us
        # creating one via Connection_connect.  (The create_database function
        # uses this facility, for example.)
        if '_CConnection' in keywords_args:
            self._C_con = keywords_args['_CConnection']
            # Since we given a pre-existing CConnection instance rather than
            # creating it ourselves, we need to explicitly give it a reference
            # to its Python companion (self):
            _k.Connection_python_wrapper_obj_set(self._C_con, self)
        else:
            n_nonkeyword = len(args)
            n_keyword = len(keywords_args)

            if n_nonkeyword == 0 and n_keyword == 0:
                raise ProgrammingError(
                    'connect() requires at least 3 keyword arguments.'
                  )
            elif n_keyword > 0 and n_nonkeyword == 0:
                source_dict = keywords_args # The typical case.
            else:
                # This case is for backward compatibility ONLY:
                import warnings # Lazy import.
                warnings.warn('The non-keyword-argument form of the connect()'
                    ' function is deprecated.  Use'
                    ' connect(dsn=..., user=..., password=...) rather than'
                    ' connect(..., ..., ...)',
                    DeprecationWarning
                  )
                if n_keyword > 0:
                    raise ProgrammingError('Do not specify both non-keyword'
                        ' args and keyword args (keyword-only is preferred).'
                      )
                elif n_nonkeyword != 3:
                    raise ProgrammingError('If using non-keyword args, must'
                        ' provide exactly 3: dsn, user, password.'
                      )
                else:
                    # Transform the argument tuple into an argument dict.
                    source_dict = {'dsn': args[0], 'user': args[1],
                        'password': args[2]
                      }

            timeout = keywords_args.pop('timeout', None)

            if timeout is not None:
                if not _CONNECTION_TIMEOUT_SUPPORTED:
                    raise ProgrammingError("The connection timeout feature is"
                        " disabled in this build."
                      )

                _connection_timeout.startTimeoutThreadIfNecessary(
                    _k.ConnectionTimeoutThread_main, _k.CTM_halt
                  )

            # Pre-render the requisite buffers (plus the dialect), then send
            # them down to the C level.  _k.Connection_connect() will give us a
            # C-level connection structure (self._C_con, of type
            # ConnectionType) in return.  self will then serve as a proxy for
            # self._C_con.
            #
            # Notice that once rendered by _build_connect_structures, the
            # connection parameters are retained in self._C_con_params in case
            # kinterbasdb's internals need to clone this connection.
            b = _DPBBuilder()
            b.buildFromParamDict(source_dict)
            self._charset = b.charset
            self._C_con_params = (b.dsn, b.dpb, b.dialect)
            self._C_con = _k.Connection_connect(self,
                b.dsn, b.dpb, b.dialect, timeout
              )

        self._normalize_type_trans()
        # 2003.03.30: Moved precision_mode up to the Python level (it's
        # deprecated).
        self._precision_mode = 0


    def __del__(self):
        # This method should not call the Python implementation of close().
        self._close_physical_connection(raiseExceptionOnError=False)


    def drop_database(self):
        """
          Drops the database to which this connection is attached.

          Unlike plain file deletion, this method behaves responsibly, in that
        it removes shadow files and other ancillary files for this database.
        """
        self._ensure_group_membership(False, "Cannot drop database via"
            " connection that is part of a ConnectionGroup."
          )
        _k.Connection_drop_database(self._C_con)


    def begin(self, tpb=None):
        """
          Starts a transaction explicitly.  This is never *required*; a
        transaction will be started implicitly if necessary.

        Parameters:
        $tpb: Optional transaction parameter buffer (TPB) populated with
            kinterbasdb.isc_tpb_* constants.  See the Interbase API guide for
            these constants' meanings.
        """
        if self.group is not None:
            self.group.begin()
            return

        if tpb is None:
            tpb = self.default_tpb
        else:
            tpb = _validateTPB(tpb)

        if not isinstance(tpb, str):
            tpb = tpb.render()

        _k.Connection_begin(self._C_con, tpb)


    def prepare(self):
        """
          Manually triggers the first phase of a two-phase commit (2PC).  Use
        of this method is optional; if preparation is not triggered manually,
        it will be performed implicitly by commit() in a 2PC.
          See also the method ConnectionGroup.prepare.
        """
        if self.group is not None:
            self.group.prepare()
            return

        _k.Connection_prepare(self._C_con)


    def commit(self, retaining=False):
        """
          Commits (permanently applies the actions that have taken place as
        part of) the active transaction.

        Parameters:
          $retaining (optional boolean that defaults to False):
              If True, the transaction is immediately cloned after it has been
            committed.  This retains system resources associated with the
            transaction and leaves undisturbed the state of any cursors open on
            this connection.  In effect, retaining commit keeps the transaction
            "open" across commits.
              See IB 6 API Guide pages 75 and 291 for more info.
        """
        if self.group is not None:
            self.group.commit(retaining=retaining)
            return

        _k.Connection_commit(self._C_con, retaining)


    def savepoint(self, name):
        """
          Establishes a SAVEPOINT named $name.
          To rollback to this SAVEPOINT, use rollback(savepoint=name).

          Example:
            con.savepoint('BEGINNING_OF_SOME_SUBTASK')
            ...
            con.rollback(savepoint='BEGINNING_OF_SOME_SUBTASK')
        """
        self.execute_immediate('SAVEPOINT ' + name)


    def rollback(self, retaining=False, savepoint=None):
        """
          Rolls back (cancels the actions that have taken place as part of) the
        active transaction.

        Parameters:
          $retaining (optional boolean that defaults to False):
              If True, the transaction is immediately cloned after it has been
            rolled back.  This retains system resources associated with the
            transaction and leaves undisturbed the state of any cursors open on
            this connection.  In effect, retaining rollback keeps the
            transaction "open" across rollbacks.
              See IB 6 API Guide pages 75 and 373 for more info.
          $savepoint (string name of the SAVEPOINT):
              If a savepoint name is supplied, only rolls back as far as that
            savepoint, rather than rolling back the entire transaction.
        """
        if savepoint is None:
            if self.group is not None:
                self.group.rollback(retaining=retaining)
                return

            _k.Connection_rollback(self._C_con, retaining)
        else:
            self.execute_immediate('ROLLBACK TO ' + savepoint)


    def execute_immediate(self, sql):
        """
          Executes a statement without caching its prepared form.  The
        statement must NOT be of a type that returns a result set.

          In most cases (especially cases in which the same statement--perhaps
        a parameterized statement--is executed repeatedly), it is better to
        create a cursor using the connection's cursor() method, then execute
        the statement using one of the cursor's execute methods.
        """
        _k.Connection_execute_immediate(self._C_con, sql)


    def database_info(self, request, result_type):
        """
          Wraps the Interbase C API function isc_database_info.

          For documentation, see the IB 6 API Guide section entitled
        "Requesting information about an attachment" (p. 51).

          Note that this method is a VERY THIN wrapper around the IB C API
        function isc_database_info.  This method does NOT attempt to interpret
        its results except with regard to whether they are a string or an
        integer.

          For example, requesting isc_info_user_names will return a string
        containing a raw succession of length-name pairs.  A thicker wrapper
        might interpret those raw results and return a Python tuple, but it
        would need to handle a multitude of special cases in order to cover
        all possible isc_info_* items.

          Note:  Some of the information available through this method would be
        more easily retrieved with the Services API (see submodule
        kinterbasdb.services).

        Parameters:
        $result_type must be either:
           's' if you expect a string result, or
           'i' if you expect an integer result
        """
        # Note:  Server-side implementation for most of isc_database_info is in
        # jrd/inf.cpp.
        res = _k.Connection_database_info(self._C_con, request, result_type)

        # 2004.12.12:
        # The result buffers for a few request codes don't follow the generic
        # conventions, so we need to return their full contents rather than
        # omitting the initial infrastructural bytes.
        if (    result_type == 's'
            and request not in _DATABASE_INFO__KNOWN_LOW_LEVEL_EXCEPTIONS
          ):
            res = res[3:]

        return res


    def db_info(self, request):
        # Contributed by Pavel Cisar; incorporated 2004.09.10; heavily modified
        # 2004.12.12.
        """
          Higher-level convenience wrapper around the database_info method that
        parses the output of database_info into Python-friendly objects instead
        of returning raw binary buffers in the case of complex result types.
        If an unrecognized code is requested, ValueError is raised.

        Parameters:
        $request must be either:
          - A single kinterbasdb.isc_info_* info request code.
            In this case, a single result is returned.
          - A sequence of such codes.
            In this case, a mapping of (info request code -> result) is
            returned.
        """
        # Notes:
        #
        # - IB 6 API Guide page 391:  "In InterBase, integer values...
        #   are returned in result buffers in a generic format where
        #   the least significant byte is first, and the most
        #   significant byte last."

        # We process request as a sequence of info codes, even if only one code
        # was supplied by the caller.
        requestIsSingleton = isinstance(request, int)
        if requestIsSingleton:
            request = (request,)

        results = {}
        for infoCode in request:
            if infoCode == isc_info_base_level:
                # (IB 6 API Guide page 52)
                buf = self.database_info(infoCode, 's')
                # Ignore the first byte.
                baseLevel = struct.unpack('B', buf[1])[0]
                results[infoCode] = baseLevel
            elif infoCode == isc_info_db_id:
                # (IB 6 API Guide page 52)
                buf = self.database_info(infoCode, 's')
                pos = 0

                conLocalityCode = struct.unpack('B', buf[pos])[0]
                pos += 1

                dbFilenameLen = struct.unpack('B', buf[1])[0]
                pos += 1

                dbFilename = buf[pos:pos+dbFilenameLen]
                pos += dbFilenameLen

                siteNameLen = struct.unpack('B', buf[pos])[0]
                pos += 1

                siteName = buf[pos:pos+siteNameLen]
                pos += siteNameLen

                results[infoCode] = (conLocalityCode, dbFilename, siteName)
            elif infoCode == isc_info_implementation:
                # (IB 6 API Guide page 52)
                buf = self.database_info(infoCode, 's')
                # Skip the first four bytes.
                pos = 1

                implNumber = struct.unpack('B', buf[pos])[0]
                pos += 1

                classNumber = struct.unpack('B', buf[pos])[0]
                pos += 1

                results[infoCode] = (implNumber, classNumber)
            elif infoCode in (isc_info_version, isc_info_firebird_version):
                # (IB 6 API Guide page 53)
                buf = self.database_info(infoCode, 's')
                # Skip the first byte.
                pos = 1

                versionStringLen = struct.unpack('B', buf[pos])[0]
                pos += 1

                versionString = buf[pos:pos+versionStringLen]

                results[infoCode] = versionString
            elif infoCode == isc_info_user_names:
                # (IB 6 API Guide page 54)
                #
                # The isc_info_user_names results buffer does not exactly match
                # the format declared on page 54 of the IB 6 API Guide.
                #   The buffer is formatted as a sequence of clusters, each of
                # which begins with the byte isc_info_user_names, followed by a
                # two-byte cluster length, followed by a one-byte username
                # length, followed by a single username.
                #   I don't understand why the lengths are represented
                # redundantly (the two-byte cluster length is always one
                # greater than the one-byte username length), but perhaps it's
                # an attempt to adhere to the general format of an information
                # cluster declared on page 51 while also [trying, but failing
                # to] adhere to the isc_info_user_names-specific format
                # declared on page 54.
                buf = self.database_info(infoCode, 's')

                usernames = []
                pos = 0
                while pos < len(buf):
                    if struct.unpack('B', buf[pos])[0] != isc_info_user_names:
                        raise OperationalError('While trying to service'
                            ' isc_info_user_names request, found unexpected'
                            ' results buffer contents at position %d of [%s]'
                            % (pos, buf)
                          )
                    pos += 1

                    # The two-byte cluster length:
                    nameClusterLen = struct.unpack('<H', buf[pos:pos+2])[0]
                    pos += 2

                    # The one-byte username length:
                    nameLen = struct.unpack('B', buf[pos])[0]
                    assert nameLen == nameClusterLen - 1
                    pos += 1

                    usernames.append(buf[pos:pos+nameLen])
                    pos += nameLen

                # The client-exposed return value is a dictionary mapping
                # username -> number of connections by that user.
                res = {}
                for un in usernames:
                    res[un] = res.get(un, 0) + 1

                results[infoCode] = res
            elif infoCode in _DATABASE_INFO_CODES_WITH_INT_RESULT:
                results[infoCode] = self.database_info(infoCode, 'i')
            elif infoCode in _DATABASE_INFO_CODES_WITH_COUNT_RESULTS:
                buf = self.database_info(infoCode, 's')
                countsByRelId = _extractDatabaseInfoCounts(buf)
                # Decided not to convert the relation IDs to relation names
                # for two reasons:
                #  1) Performance + Principle of Least Surprise
                #     If the client program is trying to do some delicate
                #     performance measurements, it's not helpful for
                #     kinterbasdb to be issuing unexpected queries behind the
                #     scenes.
                #  2) Field RDB$RELATIONS.RDB$RELATION_NAME is a CHAR field,
                #     which means its values emerge from the database with
                #     trailing whitespace, yet it's not safe in general to
                #     strip that whitespace because actual relation names can
                #     have trailing whitespace (think
                #     'create table "table1 " (f1 int)').
                results[infoCode] = countsByRelId
            elif infoCode in _DATABASE_INFO_CODES_WITH_TIMESTAMP_RESULT:
                buf = self.database_info(infoCode, 's')
                timestampTuple = raw_timestamp_to_tuple(buf)
                registeredConverter = self.get_type_trans_out()['TIMESTAMP']
                timestamp = registeredConverter(timestampTuple)
                results[infoCode] = timestamp
            else:
                raise ValueError('Unrecognized database info code %s'
                    % str(infoCode)
                  )

        if requestIsSingleton:
            return results[request[0]]
        else:
            return results


    def transaction_info(self, request, result_type):
        if not self._has_transaction():
            raise ProgrammingError('This connection has no active transaction.')

        return _k.Connection_transaction_info(self._C_con, request, result_type)


    def trans_info(self, request):
        # We process request as a sequence of info codes, even if only one code
        # was supplied by the caller.
        requestIsSingleton = isinstance(request, int)
        if requestIsSingleton:
            request = (request,)

        results = {}
        for infoCode in request:
            if infoCode == globals().get('isc_info_tra_isolation', -1):
                buf = self.transaction_info(infoCode, 's')
                buf = buf[1 + struct.calcsize('h'):]
                if len(buf) == 1:
                    results[infoCode] = portable_int(buf)
                else:
                    # For isolation level isc_info_tra_read_committed, the
                    # first byte indicates the isolation level
                    # (isc_info_tra_read_committed), while the second indicates
                    # the record version flag (isc_info_tra_rec_version or
                    # isc_info_tra_no_rec_version).
                    isolationLevelByte, recordVersionByte = struct.unpack('cc', buf)
                    isolationLevel = portable_int(isolationLevelByte)
                    recordVersion = portable_int(recordVersionByte)
                    results[infoCode] = (isolationLevel, recordVersion)
            else:
                # At the time of this writing (2006.02.09),
                # isc_info_tra_isolation is the only known return value of
                # isc_transaction_info that's not a simple integer.
                results[infoCode] = self.transaction_info(infoCode, 'i')

        if requestIsSingleton:
            return results[request[0]]
        else:
            return results


    def cursor(self):
        "Creates a new cursor that operates within the context of this"
        " connection."
        return Cursor(self)


    def close(self):
        "Closes the connection to the database server."
        self._ensure_group_membership(False, "Cannot close a connection that"
            " is a member of a ConnectionGroup."
          )
        self._close_physical_connection(raiseExceptionOnError=True)


    # closed read-only property:
    def _closed_get(self):
        return _k.Connection_closed_get(self._C_con)
    closed = property(_closed_get)


    def _close_physical_connection(self, raiseExceptionOnError=True):
        # Sever the physical connection to the database server and replace our
        # underyling _kinterbasdb.ConnectionType object with a null instance
        # of that type, so that post-close() method calls on this connection
        # will raise ProgrammingErrors, as required by the DB API Spec.
        try:
            if getattr(self, '_C_con', None) is not None:
                if (    _k
                    and self._C_con is not _k.null_connection
                    and not _k.Connection_closed_get(self._C_con)
                  ):
                    try:
                        _k.Connection_close(self._C_con)
                    except ProgrammingError:
                        if raiseExceptionOnError:
                            raise
                    self._C_con = _k.null_connection
                elif raiseExceptionOnError:
                    raise ProgrammingError('Connection is already closed.')
        except:
            if raiseExceptionOnError:
                raise


    def _has_db_handle(self):
        return self._C_con is not _k.null_connection


    def _has_transaction(self):
        # Does this connection currently have an active transaction (including
        # a distributed transaction)?
        return _k.Connection_has_transaction(self._C_con)

    def _normalize_type_trans(self):
        # Set the type translation dictionaries to their "normal" form--the
        # minumum required for standard kinterbasdb operation.
        self.set_type_trans_in(_NORMAL_TYPE_TRANS_IN)
        self.set_type_trans_out(_NORMAL_TYPE_TRANS_OUT)

    def _enforce_min_trans(self, trans_dict, translator_source):
        #   Any $trans_dict that the Python programmer supplies for a
        # Connection must have entries for at least the types listed in
        # _MINIMAL_TYPE_TRANS_TYPES, because kinterbasdb uses dynamic type
        # translation even if it is not explicitly configured by the Python
        # client programmer.
        #   The Cursor.set_type_trans* methods need not impose the same
        # requirement, because "translator resolution" will bubble upward from
        # the cursor to its connection.
        #   This method inserts the required translators into the incoming
        # $trans_dict if that $trans_dict does not already contain them.
        # Note that $translator_source will differ between in/out translators.
        for type_name in _MINIMAL_TYPE_TRANS_TYPES:
            if type_name not in trans_dict:
                trans_dict[type_name] = translator_source[type_name]

    def set_type_trans_out(self, trans_dict):
        """
          Changes the outbound type translation map.
          For more information, see the "Dynamic Type Translation" section of
        the KInterbasDB Usage Guide.
        """
        _trans_require_dict(trans_dict)
        self._enforce_min_trans(trans_dict, _NORMAL_TYPE_TRANS_OUT)
        return _k.set_Connection_type_trans_out(self._C_con, trans_dict)

    def get_type_trans_out(self):
        """
          Retrieves the outbound type translation map.
          For more information, see the "Dynamic Type Translation" section of
        the KInterbasDB Usage Guide.
        """
        return _k.get_Connection_type_trans_out(self._C_con)

    def set_type_trans_in(self, trans_dict):
        """
          Changes the inbound type translation map.
          For more information, see the "Dynamic Type Translation" section of
        the KInterbasDB Usage Guide.
        """
        _trans_require_dict(trans_dict)
        self._enforce_min_trans(trans_dict, _NORMAL_TYPE_TRANS_IN)
        return _k.set_Connection_type_trans_in(self._C_con, trans_dict)

    def get_type_trans_in(self):
        """
          Retrieves the inbound type translation map.
          For more information, see the "Dynamic Type Translation" section of
        the KInterbasDB Usage Guide.
        """
        return _k.get_Connection_type_trans_in(self._C_con)


    if not _EVENT_HANDLING_SUPPORTED:
        def event_conduit(self, event_names):
            raise NotSupportedError("Event handling was not enabled when"
                " kinterbasdb's C layer was compiled."
              )
    else:
        def event_conduit(self, event_names):
            return _k.EventConduit_create(self._C_con, self._C_con_params,
                event_names
              )


    # default_tpb read-write property:
    def _default_tpb_get(self):
        return self._default_tpb
    def _default_tpb_set(self, value):
        self._default_tpb = _validateTPB(value)
    default_tpb = property(_default_tpb_get, _default_tpb_set)

    # The C layer of KInterbasDB uses this read-only property when it needs a
    # TPB that's strictly a memory buffer, rather than potentially a TPB
    # instance.
    def __default_tpb_str_get_(self):
        defTPB = self.default_tpb
        if not isinstance(defTPB, str):
            defTPB = defTPB.render()
        return defTPB
    _default_tpb_str_ = property(__default_tpb_str_get_)


    # dialect read-write property:
    def _dialect_get(self):
        return _k.Connection_dialect_get(self._C_con)
    def _dialect_set(self, value):
        _k.Connection_dialect_set(self._C_con, value)
    dialect = property(_dialect_get, _dialect_set)


    # precision_mode read-write property (deprecated):
    def _precision_mode_get(self):
        # Postpone this warning until a later version:
        #import warnings # Lazy import.
        #warnings.warn(
        #    'precision_mode is deprecated in favor of dynamic type'
        #    ' translation (see the [set|get]_type_trans_[in|out] methods).',
        #    DeprecationWarning
        #  )
        return self._precision_mode
    def _precision_mode_set(self, value):
        # Postpone this warning until a later version:
        #import warnings # Lazy import.
        #warnings.warn(
        #    'precision_mode is deprecated in favor of dynamic type'
        #    ' translation (see the [set|get]_type_trans_[in|out] methods).',
        #    DeprecationWarning
        #  )
        value = bool(value)

        # Preserve the previous DTT settings that were in place before this
        # call to the greatest extent possible (although dynamic type
        # translation and the precision_mode attribute really aren't meant to
        # be used together).
        trans_in = self.get_type_trans_in()
        trans_out = self.get_type_trans_out()

        if value: # precise:
            trans_in['FIXED']  = fixed_conv_in_precise
            trans_out['FIXED'] = fixed_conv_out_precise
        else: # imprecise:
            trans_in['FIXED']  = fixed_conv_in_imprecise
            trans_out['FIXED'] = fixed_conv_out_imprecise

        self.set_type_trans_in(trans_in)
        self.set_type_trans_out(trans_out)

        self._precision_mode = value
    precision_mode = property(_precision_mode_get, _precision_mode_set)


    # server_version read-only property:
    def _server_version_get(self):
        return self.db_info(isc_info_version)
    server_version = property(_server_version_get)


    # charset read-only property:
    def _charset_get(self):
        return self._charset
    def _charset_set(self, value):
        # More informative error message:
        raise AttributeError("A connection's 'charset' property can be"
            " specified upon Connection creation as a keyword argument to"
            " kinterbasdb.connect, but it cannot be modified thereafter."
          )
    charset = property(_charset_get, _charset_set)


    # group read-only property:
    def _group_get(self):
        return _k.Connection_get_group(self._C_con)
    group = property(_group_get)


    def _set_group(self, group):
        # This package-private method allows ConnectionGroup's membership
        # management functionality to bypass the conceptually read-only nature
        # of the Connection.group property.
        if group is not None:
            assert _k.Connection_get_group(self._C_con) is None
        # Unless the group is being cleared (set to None), pass a *WEAK*
        # reference down to the C level (otherwise, even the cyclic garbage
        # collector can't collect ConnectionGroups or their Connections because
        # the Connections' references are held at the C level, not the Python
        # level).
        if group is None:
            _k.Connection_set_group(self._C_con, None)
        else:
            _k.Connection_set_group(self._C_con, group)


    def _ensure_group_membership(self, must_be_member, err_msg):
        if must_be_member:
            if self.group is None:
                raise ProgrammingError(err_msg)
        else:
            if not hasattr(self, 'group'):
                return
            if self.group is not None:
                raise ProgrammingError(err_msg)


    def _timeout_enabled_get(self):
        return _k.Connection_timeout_enabled(self._C_con)
    _timeout_enabled = property(_timeout_enabled_get)


    def _activity_stamps(self):
        return _k.Connection__read_activity_stamps(self._C_con)


class ConnectionGroup(object):
    # XXX: ConnectionGroup objects currently are not thread-safe.  Since
    # separate Connections can be manipulated simultaneously by different
    # threads in kinterbasdb, it would make sense for a container of multiple
    # connections to be safely manipulable simultaneously by multiple threads.

    # XXX: Adding two connections to the same database freezes the DB client
    # library.  However, I've no way to detect with certainty whether any given
    # con1 and con2 are connected to the same database, what with database
    # aliases, IP host name aliases, remote-vs-local protocols, etc.
    # Therefore, a warning must be added to the docs.

    def __init__(self, connections=()):
        _ensureInitialized()

        self._cons = []
        self._trans_handle = None

        for con in connections:
            self.add(con)


    def __del__(self):
        self.disband()


    def disband(self):
        # Notice that the ConnectionGroup rollback()s itself BEFORE releasing
        # its Connection references.
        if getattr(self, '_trans_handle', None) is not None:
            self.rollback()
        if hasattr(self, '_cons'):
            self.clear()


    # Membership methods:
    def add(self, con):
        ### CONTRAINTS ON $con: ###
        # con must be an instance of kinterbasdb.Connection:
        if not isinstance(con, Connection):
            raise TypeError('con must be an instance of'
                ' kinterbasdb.Connection'
              )
        # con cannot already be a member of this group:
        if con in self:
            raise ProgrammingError('con is already a member of this group.')
        # con cannot belong to more than one group at a time:
        if con.group:
            raise ProgrammingError('con is already a member of another group;'
                ' it cannot belong to more than one group at once.'
              )
        # con cannot be added if it has an active transaction:
        if con._has_transaction():
            raise ProgrammingError('con already has an active transaction;'
                ' that must be resolved before con can join this group.'
              )
        # con must be connected to a database; it must not have been closed.
        if not con._has_db_handle():
            raise ProgrammingError('con has been closed; it cannot join a'
                ' group.'
              )

        if con._timeout_enabled:
            raise ProgrammingError('Connections with timeout enabled cannot'
                ' participate in distributed transactions.'
              )

        ### CONTRAINTS ON $self: ###
        # self cannot accept new members while self has an unresolved
        # transaction:
        self._require_transaction_state(False,
            'Cannot add connection to group that has an unresolved'
            ' transaction.'
          )
        # self cannot have more than DIST_TRANS_MAX_DATABASES members:
        if self.count() >= DIST_TRANS_MAX_DATABASES:
            raise ProgrammingError('The database engine limits the number of'
                ' database handles that can participate in a single'
                ' distributed transaction to %d or fewer; this group already'
                ' has %d members.'
                % (DIST_TRANS_MAX_DATABASES, self.count())
              )

        ### CONTRAINTS FINISHED ###

        # Can't set con.group directly (read-only); must use package-private
        # method.
        con._set_group(self)
        self._cons.append(con)


    def remove(self, con):
        if con not in self:
            raise ProgrammingError('con is not a member of this group.')
        # The following assertion was invalidated by the introduction of weak
        # refs:
        #assert con.group is self
        self._require_transaction_state(False,
            'Cannot remove connection from group that has an unresolved'
            ' transaction.'
          )

        con._set_group(None)
        self._cons.remove(con)


    def clear(self):
        self._require_transaction_state(False,
            'Cannot clear group that has an unresolved transaction.'
          )
        for con in self.members():
            self.remove(con)
        assert self.count() == 0


    def members(self):
        return self._cons[:] # return a *copy* of the internal list


    def count(self):
        return len(self._cons)


    def contains(self, con):
        return con in self._cons
    __contains__ = contains # alias to support the 'in' operator


    def __iter__(self):
        return iter(self._cons)


    # Transactional methods:
    def _require_transaction_state(self, must_be_active, err_msg=''):
        trans_handle = self._trans_handle
        if (
               (must_be_active and trans_handle is None)
            or (not must_be_active and trans_handle is not None)
          ):
            raise ProgrammingError(err_msg)


    def _require_non_empty_group(self, operation_name):
        if self.count() == 0:
            raise ProgrammingError('Cannot %s distributed transaction with'
                ' an empty ConnectionGroup.' % operation_name
              )


    def begin(self):
        self._require_transaction_state(False,
            'Must resolve current transaction before starting another.'
          )
        self._require_non_empty_group('start')
        self._trans_handle = _k.distributed_begin(self._cons)


    def prepare(self):
        """
          Manually triggers the first phase of a two-phase commit (2PC).  Use
        of this method is optional; if preparation is not triggered manually,
        it will be performed implicitly by commit() in a 2PC.
        """
        self._require_non_empty_group('prepare')
        self._require_transaction_state(True,
            'This group has no transaction to prepare.'
          )

        _k.distributed_prepare(self._trans_handle)


    def commit(self, retaining=False):
        self._require_non_empty_group('commit')
        # The consensus among Python DB API experts is that transactions should
        # always be started implicitly, even if that means allowing a commit()
        # or rollback() without an actual transaction.
        if self._trans_handle is None:
            return

        _k.distributed_commit(self._trans_handle, retaining)
        self._trans_handle = None

        for con in self._cons: # 2005.07.22
            _k.Connection_clear_transaction_stats(con._C_con)


    def rollback(self, retaining=False):
        self._require_non_empty_group('roll back')
        # The consensus among Python DB API experts is that transactions should
        # always be started implicitly, even if that means allowing a commit()
        # or rollback() without an actual transaction.
        if self._trans_handle is None:
            return

        _k.distributed_rollback(self._trans_handle, retaining)
        self._trans_handle = None

        for con in self._cons: # 2005.07.22
            _k.Connection_clear_transaction_stats(con._C_con)


##########################################
##     PUBLIC CLASSES: END              ##
##########################################

class _RowMapping(object):
    """
      An internal kinterbasdb class that wraps a row of results in order to map
    field name to field value.

      kinterbasdb makes ABSOLUTELY NO GUARANTEES about the return value of the
    fetch(one|many|all) methods except that it is a sequence indexed by field
    position, and no guarantees about the return value of the
    fetch(one|many|all)map methods except that it is a mapping of field name
    to field value.
      Therefore, client programmers should NOT rely on the return value being
    an instance of a particular class or type.
    """

    def __init__(self, description, row):
        self._description = description
        fields = self._fields = {}
        pos = 0
        for fieldSpec in description:
            # It's possible for a result set from the database engine to return
            # multiple fields with the same name, but kinterbasdb's key-based
            # row interface only honors the first (thus setdefault, which won't
            # store the position if it's already present in self._fields).
            fields.setdefault(fieldSpec[DESCRIPTION_NAME], row[pos])
            pos += 1


    def __len__(self):
        return len(self._fields)


    def __getitem__(self, fieldName):
        fields = self._fields
        # Straightforward, unnormalized lookup will work if the fieldName is
        # already uppercase and/or if it refers to a database field whose
        # name is case-sensitive.
        if fieldName in fields:
            return fields[fieldName]
        else:
            fieldNameNormalized = _normalizeDatabaseIdentifier(fieldName)
            try:
                return fields[fieldNameNormalized]
            except KeyError:
                raise KeyError('Result set has no field named "%s".  The field'
                    ' name must be one of: (%s)'
                    % (fieldName, ', '.join(fields.keys()))
                  )


    def get(self, fieldName, defaultValue=None):
        try:
            return self[fieldName]
        except KeyError:
            return defaultValue


    def __contains__(self, fieldName):
        try:
            self[fieldName]
        except KeyError:
            return False
        else:
            return True


    def __str__(self):
        # Return an easily readable dump of this row's field names and their
        # corresponding values.
        return '<result set row with %s>' % ', '.join([
            '%s = %s' % (fieldName, self[fieldName])
            for fieldName in self._fields.keys()
          ])


    def keys(self):
        # Note that this is an *ordered* list of keys.
        return [fieldSpec[DESCRIPTION_NAME] for fieldSpec in self._description]


    def values(self):
        # Note that this is an *ordered* list of values.
        return [self[fieldName] for fieldName in self.keys()]


    def items(self):
        return [(fieldName, self[fieldName]) for fieldName in self.keys()]


    def iterkeys(self):
        for fieldDesc in self._description:
            yield fieldDesc[DESCRIPTION_NAME]

    __iter__ = iterkeys


    def itervalues(self):
        for fieldName in self:
            yield self[fieldName]


    def iteritems(self):
        for fieldName in self:
            yield fieldName, self[fieldName]


class _DPBBuilder(object):
    def buildFromParamDict(self, d):
        dsn = d.get('dsn', None)
        host = d.get('host', None)
        database = d.get('database', None)

        user = d.get('user', os.environ.get('ISC_USER', None))
        password = d.get('password', os.environ.get('ISC_PASSWORD', None))
        role = d.get('role', None)
        charset = d.get('charset', None)
        dialect = d.get('dialect', 0)
        dpbEntries = d.get('dpb_entries', ())

        self.dsn = self.buildDSNFrom(dsn, host, database)
        del dsn, host, database

        # Build <<DPB>>:begin:
        # Build the database parameter buffer.  self._dpb is a list of binary
        # strings that will be rolled up into a single binary string and
        # passed, ultimately, to the C function isc_att4ch_database as the
        # 'dpb' argument.

        self.initializeDPB()

        self.addStringIfProvided(isc_dpb_user_name, user)
        self.addStringIfProvided(isc_dpb_password, password)
        self.addStringIfProvided(isc_dpb_sql_role_name, role)

        self.charset = (charset and charset) or None
        if self.charset:
            self.addString(isc_dpb_lc_ctype, charset)

        self.processUserSuppliedDPBEntries(dpbEntries)

        self.renderDPB()

        # Leave dialect alone; the C code will validate it.
        self.dialect = dialect

        assert self.dsn is not None
        assert self.dpb is not None
        assert self.dialect is not None
        assert hasattr(self, 'charset')


    def buildDSNFrom(self, dsn, host, database):
        if (   (not dsn and not host and not database)
            or (dsn and (host or database))
            or (host and not database)
          ):
            raise ProgrammingError(
                "Must supply one of:\n"
                " 1. keyword argument dsn='host:/path/to/database'\n"
                " 2. both keyword arguments host='host' and"
                   " database='/path/to/database'\n"
                " 3. only keyword argument database='/path/to/database'"
              )

        if not dsn:
            if host and host.endswith(':'):
                raise ProgrammingError('Host must not end with a colon.'
                    ' You should specify host="%s" rather than host="%s".'
                    % (host[:-1], host)
                  )
            elif host:
                dsn = '%s:%s' % (host, database)
            else:
                dsn = database

        assert dsn, 'Internal error in _build_connect_structures DSN prep.'
        return dsn


    def initializeDPB(self):
        # Start with requisite DPB boilerplate, a single byte that informs the
        # database API what version of DPB it's dealing with:
        self._dpb = [ struct.pack('c', isc_dpb_version1) ]


    def renderDPB(self):
        self.dpb = ''.join(self._dpb)


    def addString(self, codeAsByte, s):
        # Append a string parameter to the end of the DPB.  A string parameter
        # is represented in the DPB by the following binary sequence:
        #  - a 1-byte byte code telling the purpose of the upcoming string
        #  - 1 byte telling the length of the upcoming string
        #  - the string itself
        # See IB 6 API guide page 44 for documentation of what's is going on
        # here.
        self._validateCode(codeAsByte)

        sLen = len(s)
        if sLen >= 256:
            # Because the length is denoted in the DPB by a single byte.
            raise ProgrammingError('Individual component of database'
                ' parameter buffer is too large.  Components must be less'
                ' than 256 bytes.'
              )
        format = 'cc%ds' % sLen # like 'cc50s' for a 50-byte string
        newEntry = struct.pack(format, codeAsByte, chr(sLen), s)

        self._dpb.append(newEntry)


    def addStringIfProvided(self, codeAsByte, value):
        if value:
            self.addString(codeAsByte, value)


    def addInt(self, codeAsByte, value):
        self._validateCode(codeAsByte)

        if not isinstance(value, (int, long)) or value < 0 or value > 255:
            raise ProgrammingError('The value for an integer DPB code must be'
                ' an int or long with a value between 0 and 255.'
              )

        newEntry = struct.pack('ccc', codeAsByte, '\x01', chr(value))

        self._dpb.append(newEntry)


    def processUserSuppliedDPBEntries(self, dpbEntries):
        # 'dpb_entries' is supposed to be a sequence of 2- or 3-tuples,
        # containing:
        #   (code, value[, type])
        # kinterbasdb doesn't need the type specified for codes that it already
        # recognizes, but for future codes, the user can specify the type,
        # which controls how the code is inserted into the DPB.
        for i, entry in enumerate(dpbEntries):
            codeAsByte = entry[0]
            value = entry[1]
            if len(entry) > 2:
                typeCode = entry[2]
            else:
                typeCode = None

            if typeCode is None:
                if codeAsByte in _DPB_CODES_WITH_STRING_VALUE:
                    typeCode = 's'
                elif codeAsByte in _DPB_CODE_WITH_INT_VALUE:
                    typeCode = 'i'
                else:
                    raise ProgrammingError('kinterbasdb cannot automatically'
                        ' recognize DPB code %s.  You need to supply a type'
                        ' code (either \'s\' or \'i\') as the third element of'
                        ' user-supplied DPB entry #%d.'
                        % (repr(codeAsByte), i + 1)
                      )

            if typeCode == 's':
                self.addString(codeAsByte, value)
            elif typeCode == 'i':
                self.addInt(codeAsByte, value)
            else:
                raise ProgrammingError('The supplied DPB type code must be'
                    ' either \'s\' or \'i\'.'
                  )


    def _validateCode(self, code):
        if not isinstance(code, str) or len(code) != 1:
            raise ProgrammingError('DPB code must be single-character str.')


# All DPB codes as of FB 2.0.0b1:
  # Note:  Many of these codes duplicate the functionality provided by the
  # Services API, so I've only attempted to add automatic recognition support
  # for the most useful parameters.

  # isc_dpb_version1
  # isc_dpb_cdd_pathname
  # isc_dpb_allocation
  # isc_dpb_journal
  # isc_dpb_page_size
  # isc_dpb_num_buffers
  # isc_dpb_buffer_length
  # isc_dpb_debug
  # isc_dpb_garbage_collect
  # isc_dpb_verify
  # isc_dpb_sweep
  # isc_dpb_enable_journal
  # isc_dpb_disable_journal
  # isc_dpb_dbkey_scope
  # isc_dpb_number_of_users
  # isc_dpb_trace
  # isc_dpb_no_garbage_collect
  # isc_dpb_damaged
  # isc_dpb_license
  # isc_dpb_sys_user_name : s
  # isc_dpb_encrypt_key
  # isc_dpb_activate_shadow
  # isc_dpb_sweep_interval
  # isc_dpb_delete_shadow
  # isc_dpb_force_write
  # isc_dpb_begin_log
  # isc_dpb_quit_log
  # isc_dpb_no_reserve
  # isc_dpb_user_name
  # isc_dpb_password : s
  # isc_dpb_password_enc
  # isc_dpb_sys_user_name_enc
  # isc_dpb_interp
  # isc_dpb_online_dump
  # isc_dpb_old_file_size
  # isc_dpb_old_num_files
  # isc_dpb_old_file
  # isc_dpb_old_start_page
  # isc_dpb_old_start_seqno
  # isc_dpb_old_start_file
  # isc_dpb_drop_walfile
  # isc_dpb_old_dump_id
  # isc_dpb_wal_backup_dir
  # isc_dpb_wal_chkptlen
  # isc_dpb_wal_numbufs
  # isc_dpb_wal_bufsize
  # isc_dpb_wal_grp_cmt_wait
  # isc_dpb_lc_messages : s
  # isc_dpb_lc_ctype
  # isc_dpb_cache_manager
  # isc_dpb_shutdown
  # isc_dpb_online
  # isc_dpb_shutdown_delay
  # isc_dpb_reserved
  # isc_dpb_overwrite
  # isc_dpb_sec_attach
  # isc_dpb_disable_wal
  # isc_dpb_connect_timeout : i
  # isc_dpb_dummy_packet_interval : i
  # isc_dpb_gbak_attach
  # isc_dpb_sql_role_name
  # isc_dpb_set_page_buffers
  # isc_dpb_working_directory
  # isc_dpb_sql_dialect : i
  # isc_dpb_set_db_readonly
  # isc_dpb_set_db_sql_dialect : i
  # isc_dpb_gfix_attach
  # isc_dpb_gstat_attach
  # isc_dpb_set_db_charset : s

_DPB_CODES_WITH_STRING_VALUE = (
    isc_dpb_user_name,
    isc_dpb_password,
    isc_dpb_lc_messages,
    isc_dpb_set_db_charset,
  )

_DPB_CODE_WITH_INT_VALUE = (
    isc_dpb_connect_timeout,
    isc_dpb_dummy_packet_interval,
    isc_dpb_sql_dialect,
    isc_dpb_set_db_sql_dialect,
  )


def _trans_require_dict(obj):
    if not isinstance(obj, dict):
        raise TypeError(
            "The dynamic type translation table must be a dictionary, not a %s"
            % ( (hasattr(obj, '__class__') and obj.__class__.__name__)
                or str(type(obj))
              )
          )


_OUT_TRANS_FUNC_SAMPLE_ARGS = {
    'TEXT':             'sample',
    'TEXT_UNICODE':     ('sample', 3),
    'BLOB':             'sample',
    'INTEGER':          1,
    'FLOATING':         1.0,
    'FIXED':            (10, -1),
    'DATE':             (2003,12,31),
    'TIME':             (23,59,59),
    'TIMESTAMP':        (2003,12,31,23,59,59),
  }

def _make_output_translator_return_type_dict_from_trans_dict(trans_dict):
    # This Python function is called from the C level; don't remove it.
    #
    # Calls each output translator in trans_dict, passing the translator sample
    # arguments and recording its return type.
    # Returns a mapping of translator key -> return type.
    trans_return_types = {}
    for (trans_key, translator) in trans_dict.items():
        if isinstance(trans_key, int):
            # The type entry in Cursor.description is not updated properly to
            # reflect *positional* DTT settings, and I can think of no
            # reasonable way to correct that.
            continue

        # Follow this path for any 'BLOB' DTT with a dict translator--the
        # contents of the dict will be validated later, at the C level.
        if trans_key == 'BLOB' and isinstance(translator, dict):
            if translator.get('mode', None) == 'stream':
                trans_return_types[trans_key] = BlobReader
            continue

        if translator is None:
            # Don't make an entry for "naked" translators; the
            # Cursor.description creation code will fall back on the default
            # type.
            continue

        try:
            sample_arg = _OUT_TRANS_FUNC_SAMPLE_ARGS[trans_key]
        except KeyError:
            raise ProgrammingError(
                "Cannot translate type '%s'. Type must be one of %s."
                % (trans_key, _OUT_TRANS_FUNC_SAMPLE_ARGS.keys())
              )
        return_val = translator(sample_arg)
        return_type = type(return_val)
        trans_return_types[trans_key] = return_type
    return trans_return_types


class TPB(_RequestBufferBuilder):
    def __init__(self):
        _RequestBufferBuilder.__init__(self)

        self._access_mode = isc_tpb_write

        self._isolation_level = isc_tpb_concurrency

        self._lock_resolution = isc_tpb_wait
        self._lock_timeout = None

        self._table_reservation = None

    def copy(self):
        # A shallow copy of self would be entirely safe except that
        # .table_reservation is a complex object that needs to be copied
        # separately.
        import copy

        other = copy.copy(self)
        if self._table_reservation is not None:
            other._table_reservation = copy.copy(self._table_reservation)
        return other

    def render(self):
        # YYY: Optimization:  Could memoize the rendered TPB str.
        self.clear()

        self._addCode(isc_tpb_version3)

        self._addCode(self._access_mode)

        il = self._isolation_level
        if not isinstance(il, tuple):
            il = (il,)
        for code in il:
            self._addCode(code)

        self._addCode(self._lock_resolution)
        if self._lock_timeout is not None:
            self._addCode(isc_tpb_lock_timeout)
            self._addRaw(struct.pack(
                # One bytes tells the size of the following value; an unsigned
                # int tells the number of seconds to wait before timing out.
                '<bI', struct.calcsize('I'), self._lock_timeout
              ))

        if self._table_reservation is not None:
            self._addRaw(self._table_reservation.render())

        return _RequestBufferBuilder.render(self)

    # access_mode property:
    def _get_access_mode(self):
        return self._access_mode
    def _set_access_mode(self, access_mode):
        if access_mode not in (isc_tpb_read, isc_tpb_write):
            raise ProgrammingError('Access mode must be one of'
                ' (isc_tpb_read, isc_tpb_write).'
              )
        self._access_mode = access_mode
    access_mode = property(_get_access_mode, _set_access_mode)

    # isolation_level property:
    def _get_isolation_level(self):
        return self._isolation_level
    def _set_isolation_level(self, isolation_level):
        if isinstance(isolation_level, tuple):
            if len(isolation_level) != 2:
                raise ProgrammingError('The tuple variant of isolation level'
                    ' must have two elements:  isc_tpb_read_committed in the'
                    ' first element and one of (isc_tpb_rec_version,'
                    ' isc_tpb_no_rec_version) in the second.'
                  )
            isolation_level, suboption = isolation_level
        elif isolation_level == isc_tpb_read_committed:
            suboption = isc_tpb_rec_version

        if isolation_level not in (
            isc_tpb_concurrency, isc_tpb_consistency, isc_tpb_read_committed
          ):
            raise ProgrammingError('Isolation level must be one of'
                ' (isc_tpb_concurrency, isc_tpb_consistency,'
                ' isc_tpb_read_committed).'
              )

        if isolation_level == isc_tpb_read_committed:
            if suboption not in (isc_tpb_rec_version, isc_tpb_no_rec_version):
                raise ProgrammingError('With isolation level'
                    ' isc_tpb_read_committed, suboption must be one of'
                    ' (isc_tpb_rec_version, isc_tpb_no_rec_version).'
                  )
            isolation_level = isolation_level, suboption

        self._isolation_level = isolation_level
    isolation_level = property(_get_isolation_level, _set_isolation_level)

    # lock_resolution property:
    def _get_lock_resolution(self):
        return self._lock_resolution
    def _set_lock_resolution(self, lock_resolution):
        if lock_resolution not in (isc_tpb_wait, isc_tpb_nowait):
            raise ProgrammingError('Lock resolution must be one of'
                ' (isc_tpb_wait, isc_tpb_nowait).'
              )
        self._lock_resolution = lock_resolution
    lock_resolution = property(_get_lock_resolution, _set_lock_resolution)

    # lock_timeout property:
    def _get_lock_timeout(self):
        return self._lock_timeout
    def _set_lock_timeout(self, lock_timeout):
        if lock_timeout is not None:
            UINT_MAX = 2 ** (struct.calcsize('I') * 8) - 1
            if (not isinstance(lock_timeout, (int, long))) or (
                lock_timeout < 0 or lock_timeout > UINT_MAX
              ):
                raise ProgrammingError('Lock resolution must be either None'
                    ' or a non-negative int number of seconds between 0 and'
                    ' %d.' % UINT_MAX
                  )

        self._lock_timeout = lock_timeout
    lock_timeout = property(_get_lock_timeout, _set_lock_timeout)

    # table_reservation property (an instance of TableReservation):
    def _get_table_reservation(self):
        if self._table_reservation is None:
            self._table_reservation = TableReservation()
        return self._table_reservation
    def _set_table_reservation_access(self, _):
        raise ProgrammingError('Instead of changing the value of the'
            ' .table_reservation object itself, you must change its *elements*'
            ' by manipulating it as though it were a dictionary that mapped'
            '\n  "TABLE_NAME": (sharingMode, accessMode)'
            '\nFor example:'
            '\n  tpbBuilder.table_reservation["MY_TABLE"] ='
            ' (kinterbasdb.isc_tpb_protected, kinterbasdb.isc_tpb_lock_write)'
          )
    table_reservation = property(
        _get_table_reservation, _set_table_reservation_access
      )


class TableReservation(object):
    _MISSING = object()
    _SHARING_MODE_STRS = {
        isc_tpb_shared:    'isc_tpb_shared',
        isc_tpb_protected: 'isc_tpb_protected',
        isc_tpb_exclusive: 'isc_tpb_exclusive',
      }
    _ACCESS_MODE_STRS = {
        isc_tpb_lock_read:  'isc_tpb_lock_read',
        isc_tpb_lock_write: 'isc_tpb_lock_write',
      }

    def __init__(self):
        self._res = {}

    def copy(self):
        # A shallow copy is fine.
        import copy
        return copy.copy(self)

    def render(self):
        if not self:
            return ''

        frags = []
        _ = frags.append
        for tableName, resDefs in self.iteritems():
            tableNameLenWithTerm = len(tableName) + 1
            for (sharingMode, accessMode) in resDefs:
                _(sharingMode)
                _(accessMode)
                _(struct.pack('<b%ds' % tableNameLenWithTerm,
                    tableNameLenWithTerm, tableName
                  ))

        return ''.join(frags)

    def __len__(self):
        return sum([len(item) for item in self._res.items()])

    def __nonzero__(self):
        return len(self) != 0

    def __getitem__(self, key):
        key = self._validateKey(key)

        if key in self._res:
            return self._res[key]
        else:
            nonNormalizedKey = key
            key = _normalizeDatabaseIdentifier(key)
            try:
                return self._res[key]
            except KeyError:
                raise KeyError('No table named "%s" is present.'
                    % nonNormalizedKey
                  )

    def get(self, key, default=None):
        try:
            return self[key]
        except (KeyError, TypeError):
            return default

    def __contains__(self, key):
        return (
            self.get(key, TableReservation._MISSING)
            is not TableReservation._MISSING
          )

    def __str__(self):
        if not self:
            return '<TableReservation with no entries>'

        frags = ['<TableReservation with entries:\n']
        _ = frags.append
        for tableName, resDefs in self.iteritems():
            _('  "%s":\n' % tableName)
            for rd in resDefs:
                sharingModeStr = TableReservation._SHARING_MODE_STRS[rd[0]]
                accessModeStr = TableReservation._ACCESS_MODE_STRS[rd[1]]
                _('    (%s, %s)\n' % (sharingModeStr, accessModeStr))
        _('>')
        return ''.join(frags)

    def keys(self):
        return self._res.keys()

    def values(self):
        return self._res.values()

    def items(self):
        return self._res.items()

    def iterkeys(self):
        return self._res.iterkeys()

    def itervalues(self):
        return self._res.itervalues()

    def iteritems(self):
        return self._res.iteritems()

    def __setitem__(self, key, value):
        key = self._validateKey(key)
        key = _normalizeDatabaseIdentifier(key)

        # If the += operator is being applied, the form of value will be like:
        #   [(sharingMode0, accessMode0), ..., newSharingMode, newAccessMode]
        # For the sake of convenience, we detect this situation and handle it
        # "naturally".
        if isinstance(value, list) and len(value) >= 3:
            otherValues = value[:-2]
            value = tuple(value[-2:])
        else:
            otherValues = None

        if (
               (not isinstance(value, tuple))
            or len(value) != 2
            or value[0] not in
                 (isc_tpb_shared, isc_tpb_protected, isc_tpb_exclusive)
            or value[1] not in (isc_tpb_lock_read, isc_tpb_lock_write)
          ):
            raise ValueError('Table reservation entry must be a 2-tuple of'
                ' the following form:\n'
                'element 0: sharing mode (one of (isc_tpb_shared,'
                  ' isc_tpb_protected, isc_tpb_exclusive))\n'
                'element 1: access mode (one of (isc_tpb_lock_read,'
                  ' isc_tpb_lock_write))\n'
                '%s is not acceptable.' % str(value)
              )

        if otherValues is None:
            value = [value]
        else:
            otherValues.append(value)
            value = otherValues

        self._res[key] = value

    def _validateKey(self, key):
        keyMightBeAcceptable = isinstance(key, basestring)
        if keyMightBeAcceptable and isinstance(key, unicode):
            try:
                key = key.encode('ASCII')
            except UnicodeEncodeError:
                keyMightBeAcceptable = False

        if not keyMightBeAcceptable:
            raise TypeError('Only str keys are allowed.')

        return key


def _validateTPB(tpb):
    if isinstance(tpb, TPB):
        # TPB's accessor methods perform their own validation, and its
        # render method takes care of infrastructural trivia.
        return tpb
    elif not (isinstance(tpb, str) and len(tpb) > 0):
        raise ProgrammingError('TPB must be non-unicode string of length > 0')
    # The kinterbasdb documentation promises (or at least strongly implies)
    # that if the user tries to set a TPB that does not begin with
    # isc_tpb_version3, kinterbasdb will automatically supply that
    # infrastructural value.  This promise might cause problems in the future,
    # when isc_tpb_version3 is superseded.  A possible solution would be to
    # check the first byte against all known isc_tpb_versionX version flags,
    # like this:
    #   if tpb[0] not in (isc_tpb_version3, ..., isc_tpb_versionN):
    #      tpb = isc_tpb_version3 + tpb
    # That way, compatibility with old versions of the DB server would be
    # maintained, but client code could optionally specify a newer TPB version.
    if tpb[0] != isc_tpb_version3:
        tpb = isc_tpb_version3 + tpb
    return tpb

def _normalizeDatabaseIdentifier(ident):
    if ident.startswith('"') and ident.endswith('"'):
        # Quoted name; leave the case of the field name untouched, but
        # strip the quotes.
        return ident[1:-1]
    else:
        # Everything else is normalized to uppercase to support case-
        # insensitive lookup.
        return ident.upper()

# Contributed by Pavel Cisar; incorporated 2004.09.10:
# Connection.db_info support:

# Conditionally add codes that aren't supported by all modern versions of the
# database engine:
def _addDatabaseInfoCodeIfPresent(name, addToList):
    globalz = globals()
    if name in globalz:
        addToList.append(globalz[name])

# Int codes:
_DATABASE_INFO_CODES_WITH_INT_RESULT = [
    isc_info_allocation, isc_info_no_reserve, isc_info_db_sql_dialect,
    isc_info_ods_minor_version, isc_info_ods_version, isc_info_page_size,
    isc_info_current_memory, isc_info_forced_writes, isc_info_max_memory,
    isc_info_num_buffers, isc_info_sweep_interval, isc_info_limbo,
    isc_info_attachment_id, isc_info_fetches, isc_info_marks, isc_info_reads,
    isc_info_writes, isc_info_set_page_buffers, isc_info_db_read_only,
    isc_info_db_size_in_pages, isc_info_page_errors, isc_info_record_errors,
    isc_info_bpage_errors, isc_info_dpage_errors, isc_info_ipage_errors,
    isc_info_ppage_errors, isc_info_tpage_errors,
  ]

def _addIntDatabaseInfoCodeIfPresent(name):
    _addDatabaseInfoCodeIfPresent(name, _DATABASE_INFO_CODES_WITH_INT_RESULT)

_addIntDatabaseInfoCodeIfPresent('isc_info_oldest_transaction')
_addIntDatabaseInfoCodeIfPresent('isc_info_oldest_active')
_addIntDatabaseInfoCodeIfPresent('isc_info_oldest_snapshot')
_addIntDatabaseInfoCodeIfPresent('isc_info_next_transaction')

_addIntDatabaseInfoCodeIfPresent('isc_info_active_tran_count')

del _addIntDatabaseInfoCodeIfPresent

_DATABASE_INFO_CODES_WITH_INT_RESULT = tuple(
    _DATABASE_INFO_CODES_WITH_INT_RESULT
  )

_DATABASE_INFO_CODES_WITH_COUNT_RESULTS = (
    isc_info_backout_count, isc_info_delete_count, isc_info_expunge_count,
    isc_info_insert_count, isc_info_purge_count, isc_info_read_idx_count,
    isc_info_read_seq_count, isc_info_update_count
  )

# Timestamp codes:
_DATABASE_INFO_CODES_WITH_TIMESTAMP_RESULT = []

def _addTimestampDatabaseInfoCodeIfPresent(name):
    _addDatabaseInfoCodeIfPresent(name,
        _DATABASE_INFO_CODES_WITH_TIMESTAMP_RESULT
      )

_addTimestampDatabaseInfoCodeIfPresent('isc_info_creation_date')

del _addTimestampDatabaseInfoCodeIfPresent

_DATABASE_INFO_CODES_WITH_TIMESTAMP_RESULT = tuple(
    _DATABASE_INFO_CODES_WITH_TIMESTAMP_RESULT
  )


_DATABASE_INFO__KNOWN_LOW_LEVEL_EXCEPTIONS = (
    isc_info_user_names,
  )

def _extractDatabaseInfoCounts(buf):
    # Extract a raw binary sequence of (unsigned short, signed int) pairs into
    # a corresponding Python dictionary.
    uShortSize = struct.calcsize('<H')
    intSize = struct.calcsize('<i')
    pairSize = uShortSize + intSize
    pairCount = len(buf) / pairSize

    counts = {}
    for i in range(pairCount):
        bufForThisPair = buf[i*pairSize:(i+1)*pairSize]
        relationId = struct.unpack('<H', bufForThisPair[:uShortSize])[0]
        count      = struct.unpack('<i', bufForThisPair[uShortSize:])[0]
        counts[relationId] = count
    return counts

def _look_up_array_descriptor(con, relName, fieldName): # 2006.01.30
    # This function is just a "lazy import proxy" for the
    # _array_descriptor.look_up_array_descriptor function.
    import _array_descriptor
    return _array_descriptor.look_up_array_descriptor(con, relName, fieldName)

def _look_up_array_subtype(con, relName, fieldName): # 2006.01.30
    # This function is just a "lazy import proxy" for the
    # _array_descriptor.look_up_array_subtype function.
    import _array_descriptor
    return _array_descriptor.look_up_array_subtype(con, relName, fieldName)

def _Cursor_execute_exception_type_filter(rawCode, sqlCode, msgSegments):
    # Reactivate this code if msgSegments is used in the future:
    # if not isinstance(msgSegments, list):
        # msgSegments = [msgSegments]

    if rawCode in _TRANSACTION_CONFLICT_RAW_CODES:
        return TransactionConflict

_TRANSACTION_CONFLICT_RAW_CODES = (
    # Transaction conflict table (drawn from the error table at
    # http://firebird.sourceforge.net/doc/contrib/fb_1_5_errorcodes.pdf):
    # SQLCode, Raw Code,  Description
    #--------------------------------------------------------------------------
    # -913
      335544336,
    # deadlock:  Deadlock
    #
    # -901
      335544345,
    # lock_conflict:  Lock conflict on no wait transaction
    #
    # -901
      335544383,
    # fatal_conflict:  Unrecoverable conflict with limbo transaction <number>
    #
    # -904
      335544451,
    # update_conflict:  Update conflicts with concurrent update
    #
    # -615
      335544475,
    # relation_lock:  Lock on table <string> conflicts with existing lock
    #
    # -615
      335544476,
    # record_lock:  Requested record lock conflicts with existing lock
    #
    # -901
      335544510,
    # lock_timeout:  lock time-out on wait transaction
    #--------------------------------------------------------------------------
  )
