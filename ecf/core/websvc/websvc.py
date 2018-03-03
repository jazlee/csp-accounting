import re
import os
import sys
import time
import urllib
import socket
import logging
import StringIO
import cStringIO
import mimetools
import mimetypes
import traceback
import elixir as el
from email.Utils import formatdate

DEFAULT_ERROR_MESSAGE = """\
<head>
<title>Error response</title>
</head>
<body>
<h1>Error response</h1>
<p>Error code %(code)d.
<p>Message: %(message)s.
<p>Error code explanation: %(code)s = %(explain)s.
</body>
"""

def http_date(epoch_seconds=None):
    """
    Formats the time to match the RFC1123 date format as specified by HTTP
    RFC2616 section 3.3.1.

    Accepts a floating point number expressed in seconds since the epoch, in
    UTC - such as that outputted by time.time(). If set to None, defaults to
    the current time.

    Outputs a string in the format 'Wdy, DD Mon YYYY HH:MM:SS GMT'.
    """
    rfcdate = formatdate(epoch_seconds)
    return '%s GMT' % rfcdate[:25]

class ECFWSGIRequestHandler:
  """Dispatches URLs using patterns from a URLMatcher, which is created by
  loading an application's configuration file. Executes CGI scripts in the
  local process so the scripts can use mock versions of APIs.

  HTTP requests that correctly specify a user info cookie
  (appserver_login.COOKIE_NAME) will have the 'USER_EMAIL' environment
  variable set accordingly. If the user is also an admin, the
  'USER_IS_ADMIN' variable will exist and be set to '1'. If the user is not
  logged in, 'USER_EMAIL' will be set to the empty string.

  On each request, raises an InvalidAppConfigError exception if the
  application configuration file in the directory specified by the root_path
  argument is invalid.
  """
  server_version = 'ECFWSGIServer/1.0'

  def __init__(self, _internal_header, _internal_body, _client_address, server):
    """Initializer.

    Args:
      args, kwargs: Positional and keyword arguments passed to the constructor
        of the super class.
    """
    self.rfile = StringIO.StringIO(_internal_body)
    self.wfile = StringIO.StringIO()
    self._internal_header = _internal_header
    self.client_address = _client_address
    self.server = server
    try:
        self.setup()
        self.handle()
        self.finish()
    finally:
        sys.exc_traceback = None    # Help garbage collection

  def parse_request(self):
    """Parse a request (internal).

    The request should be stored in self.raw_requestline; the results
    are in self.command, self.path, self.request_version and
    self.headers.

    Return True for success, False for failure; on failure, an
    error is sent back.

    """
    self.command = None  # set in case of error on the first line
    self.request_version = version = "HTTP/1.1" # Default
    self.close_connection = 1
    req_line = self.raw_requestline.split("\r\n")
    requestline = req_line[0]
    if requestline[-2:] == '\r\n':
        requestline = requestline[:-2]
    elif requestline[-1:] == '\n':
        requestline = requestline[:-1]
    self.requestline = requestline
    words = requestline.split()
    if len(words) == 3:
        [command, path, version] = words
        if version[:5] != 'HTTP/':
            self.send_error(400, "Bad request version (%r)" % version)
            return False
        try:
            base_version_number = version.split('/', 1)[1]
            version_number = base_version_number.split(".")
            # RFC 2145 section 3.1 says there can be only one "." and
            #   - major and minor numbers MUST be treated as
            #      separate integers;
            #   - HTTP/2.4 is a lower version than HTTP/2.13, which in
            #      turn is lower than HTTP/12.3;
            #   - Leading zeros MUST be ignored by recipients.
            if len(version_number) != 2:
                raise ValueError
            version_number = int(version_number[0]), int(version_number[1])
        except (ValueError, IndexError):
            self.send_error(400, "Bad request version (%r)" % version)
            return False
        if version_number >= (1, 1) and self.protocol_version >= "HTTP/1.1":
            self.close_connection = 0
        if version_number >= (2, 0):
            self.send_error(505,
                      "Invalid HTTP Version (%s)" % base_version_number)
            return False
    elif len(words) == 2:
        [command, path] = words
        self.close_connection = 1
        if command != 'GET':
            self.send_error(400,
                            "Bad HTTP/1.1 request type (%r)" % command)
            return False
    elif not words:
        return False
    else:
        self.send_error(400, "Bad request syntax (%r)" % requestline)
        return False
    self.command, self.path, self.request_version = command, path, version

    # Examine the headers and look for a Connection directive
    self.headers = self.MessageClass(self.rfile, 0)

    conntype = self.headers.get('Connection', "")
    if conntype.lower() == 'close':
        self.close_connection = 1
    elif (conntype.lower() == 'keep-alive' and
          self.protocol_version >= "HTTP/1.1"):
        self.close_connection = 0
    return True

  def send_error(self, code, message=None):
    """Send and log an error reply.

    Arguments are the error code, and a detailed message.
    The detailed message defaults to the short entry matching the
    response code.

    This sends an error response (so it must be called before any
    output has been generated), logs the error, and finally sends
    a piece of HTML explaining the error to the user.

    """

    try:
        short, long = self.responses[code]
    except KeyError:
        short, long = '???', '???'
    if message is None:
        message = short
    explain = long
    self.log_error("code %d, message %s", code, message)
    # using _quote_html to prevent Cross Site Scripting attacks (see bug #1100201)
    content = (self.error_message_format %
               {'code': code, 'message': _quote_html(message), 'explain': explain})
    self.send_response(code, message)
    self.send_header("Content-Type", "text/html")
    self.send_header('Connection', 'close')
    self.end_headers()
    if self.command != 'HEAD' and code >= 200 and code not in (204, 304):
        self.wfile.write(content)

  error_message_format = DEFAULT_ERROR_MESSAGE

  def send_response(self, code, message=None):
    """Send the response header and log the response code.

    Also send two standard headers with the server software
    version and the current date.

    """
    self.log_request(code)
    if message is None:
        if code in self.responses:
            message = self.responses[code][0]
        else:
            message = ''
    if self.request_version != 'HTTP/0.9':
        self.wfile.write("%s %d %s\r\n" %
                         (self.protocol_version, code, message))
        # print (self.protocol_version, code, message)
    self.send_header('Server', self.version_string())
    self.send_header('Date', self.date_time_string())

  def send_header(self, keyword, value):
    """Send a MIME header."""
    if self.request_version != 'HTTP/0.9':
      self.wfile.write("%s: %s\r\n" % (keyword, value))

    if keyword.lower() == 'connection':
      if value.lower() == 'close':
          self.close_connection = 1
      elif value.lower() == 'keep-alive':
          self.close_connection = 0

  def end_headers(self):
    """Send the blank line ending the MIME headers."""
    if self.request_version != 'HTTP/0.9':
        self.wfile.write("\r\n")

  def log_request(self, code='-', size='-'):
    """Log an accepted request.

    This is called by send_response().

    self.log_message('"%s" %s %s',
                     self.requestline, str(code), str(size))

    """
    pass

  def version_string(self):
    """Return the server software version string."""
    return self.server_version

  def date_time_string(self, timestamp=None):
    """Return the current date and time formatted for a message header."""
    if timestamp is None:
        timestamp = time.time()
    year, month, day, hh, mm, ss, wd, y, z = time.gmtime(timestamp)
    s = "%s, %02d %3s %4d %02d:%02d:%02d GMT" % (
            self.weekdayname[wd],
            day, self.monthname[month], year,
            hh, mm, ss)
    return s

  def log_date_time_string(self):
    """Return the current time formatted for logging."""
    now = time.time()
    year, month, day, hh, mm, ss, x, y, z = time.localtime(now)
    s = "%02d/%3s/%04d %02d:%02d:%02d" % (
            day, self.monthname[month], year, hh, mm, ss)
    return s

  weekdayname = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

  monthname = [None,
             'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
             'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

  # Essentially static class variables

  # The version of the HTTP protocol we support.
  # Set this to HTTP/1.1 to enable automatic keepalive
  protocol_version = "HTTP/1.1"

  # The Message-like class used to parse headers
  MessageClass = mimetools.Message

  # Table mapping response codes to messages; entries have the
  # form {code: (shortmessage, longmessage)}.
  # See RFC 2616.
  responses = {
    100: ('Continue', 'Request received, please continue'),
    101: ('Switching Protocols',
          'Switching to new protocol; obey Upgrade header'),

    200: ('OK', 'Request fulfilled, document follows'),
    201: ('Created', 'Document created, URL follows'),
    202: ('Accepted',
          'Request accepted, processing continues off-line'),
    203: ('Non-Authoritative Information', 'Request fulfilled from cache'),
    204: ('No Content', 'Request fulfilled, nothing follows'),
    205: ('Reset Content', 'Clear input form for further input.'),
    206: ('Partial Content', 'Partial content follows.'),

    300: ('Multiple Choices',
          'Object has several resources -- see URI list'),
    301: ('Moved Permanently', 'Object moved permanently -- see URI list'),
    302: ('Found', 'Object moved temporarily -- see URI list'),
    303: ('See Other', 'Object moved -- see Method and URL list'),
    304: ('Not Modified',
          'Document has not changed since given time'),
    305: ('Use Proxy',
          'You must use proxy specified in Location to access this '
          'resource.'),
    307: ('Temporary Redirect',
          'Object moved temporarily -- see URI list'),

    400: ('Bad Request',
          'Bad request syntax or unsupported method'),
    401: ('Unauthorized',
          'No permission -- see authorization schemes'),
    402: ('Payment Required',
          'No payment -- see charging schemes'),
    403: ('Forbidden',
          'Request forbidden -- authorization will not help'),
    404: ('Not Found', 'Nothing matches the given URI'),
    405: ('Method Not Allowed',
          'Specified method is invalid for this server.'),
    406: ('Not Acceptable', 'URI not available in preferred format.'),
    407: ('Proxy Authentication Required', 'You must authenticate with '
          'this proxy before proceeding.'),
    408: ('Request Timeout', 'Request timed out; try again later.'),
    409: ('Conflict', 'Request conflict.'),
    410: ('Gone',
          'URI no longer exists and has been permanently removed.'),
    411: ('Length Required', 'Client must specify Content-Length.'),
    412: ('Precondition Failed', 'Precondition in headers is false.'),
    413: ('Request Entity Too Large', 'Entity is too large.'),
    414: ('Request-URI Too Long', 'URI is too long.'),
    415: ('Unsupported Media Type', 'Entity body in unsupported format.'),
    416: ('Requested Range Not Satisfiable',
          'Cannot satisfy request range.'),
    417: ('Expectation Failed',
          'Expect condition could not be satisfied.'),

    500: ('Internal Server Error', 'Server got itself in trouble'),
    501: ('Not Implemented',
          'Server does not support this operation'),
    502: ('Bad Gateway', 'Invalid responses from another server/proxy.'),
    503: ('Service Unavailable',
          'The server cannot process the request due to a high load'),
    504: ('Gateway Timeout',
          'The gateway server did not receive a timely response'),
    505: ('HTTP Version Not Supported', 'Cannot fulfill request.'),
    }

  def setup(self):
    pass

  def finish(self):
    if not self.wfile.closed:
        self.wfile.flush()
    self.rfile.close()

  def get_environ(self):
    env = self.server.base_environ.copy()
    env['wsgi.root_path'] = self.server.root_path
    env['SERVER_PROTOCOL'] = self.request_version
    env['REQUEST_METHOD'] = self.command
    if '?' in self.path:
        path,query = self.path.split('?',1)
    else:
        path,query = self.path,''

    env['PATH_INFO'] = urllib.unquote(path)
    env['QUERY_STRING'] = query
    env['REMOTE_ADDR'] = self.client_address[0]

    if self.headers.typeheader is None:
        env['CONTENT_TYPE'] = self.headers.type
    else:
        env['CONTENT_TYPE'] = self.headers.typeheader

    length = self.headers.getheader('content-length')
    if length:
        env['CONTENT_LENGTH'] = length

    for h in self.headers.headers:
        k,v = h.split(':',1)
        k=k.replace('-','_').upper(); v=v.strip()
        if k in env:
            continue                    # skip content length, type,etc.
        if 'HTTP_'+k in env:
            env['HTTP_'+k] += ','+v     # comma-separate multiple headers
        else:
            env['HTTP_'+k] = v
    return env

  def get_stderr(self):
    return sys.stderr

  def log_error(self, format, *args):
    """Redirect error messages through the logging module."""
    logging.error(format, *args)

  def log_message(self, format, *args):
    """Redirect log messages through the logging module."""
    logging.info(format, *args)

  def handle(self):
    """Handle a single HTTP request"""

    self.raw_requestline = self._internal_header
    if not self.parse_request(): # An error code has been sent, just exit
        return

    handler = ServerHandler(
        self.rfile, self.wfile, self.get_stderr(), self.get_environ()
    )
    handler.request_handler = self      # backpointer for logging
    handler.run(self.server.get_app())

# Regular expression that matches `special' characters in parameters, the
# existence of which force quoting of the parameter value.
tspecials = re.compile(r'[ \(\)<>@,;:\\"/\[\]\?=]')

def _formatparam(param, value=None, quote=1):
    """Convenience function to format and return a key=value pair.

    This will quote the value if needed or if quote is true.
    """
    if value is not None and len(value) > 0:
        if quote or tspecials.search(value):
            value = value.replace('\\', '\\\\').replace('"', r'\"')
            return '%s="%s"' % (param, value)
        else:
            return '%s=%s' % (param, value)
    else:
        return param

def guess_scheme(environ):
    """Return a guess for whether 'wsgi.url_scheme' should be 'http' or 'https'
    """
    if environ.get("HTTPS") in ('yes','on','1'):
        return 'https'
    else:
        return 'http'

class Headers(object):
    """Manage a collection of HTTP response headers"""
    def __init__(self,headers):
        if not isinstance(headers, list):
            raise TypeError("Headers must be a list of name/value tuples")
        self._headers = headers

    def __len__(self):
        """Return the total number of headers, including duplicates."""
        return len(self._headers)

    def __setitem__(self, name, val):
        """Set the value of a header."""
        del self[name]
        self._headers.append((name, val))

    def __delitem__(self,name):
        """Delete all occurrences of a header, if present.

        Does *not* raise an exception if the header is missing.
        """
        name = name.lower()
        self._headers[:] = [kv for kv in self._headers if kv[0].lower()<>name]

    def __getitem__(self,name):
        """Get the first header value for 'name'

        Return None if the header is missing instead of raising an exception.

        Note that if the header appeared multiple times, the first exactly which
        occurrance gets returned is undefined.  Use getall() to get all
        the values matching a header field name.
        """
        return self.get(name)

    def has_key(self, name):
        """Return true if the message contains the header."""
        return self.get(name) is not None

    __contains__ = has_key

    def get_all(self, name):
        """Return a list of all the values for the named field.

        These will be sorted in the order they appeared in the original header
        list or were added to this instance, and may contain duplicates.  Any
        fields deleted and re-inserted are always appended to the header list.
        If no fields exist with the given name, returns an empty list.
        """
        name = name.lower()
        return [kv[1] for kv in self._headers if kv[0].lower()==name]


    def get(self,name,default=None):
        """Get the first header value for 'name', or return 'default'"""
        name = name.lower()
        for k,v in self._headers:
            if k.lower()==name:
                return v
        return default

    def keys(self):
        """Return a list of all the header field names.

        These will be sorted in the order they appeared in the original header
        list, or were added to this instance, and may contain duplicates.
        Any fields deleted and re-inserted are always appended to the header
        list.
        """
        return [k for k, v in self._headers]

    def values(self):
        """Return a list of all header values.

        These will be sorted in the order they appeared in the original header
        list, or were added to this instance, and may contain duplicates.
        Any fields deleted and re-inserted are always appended to the header
        list.
        """
        return [v for k, v in self._headers]

    def items(self):
        """Get all the header fields and values.

        These will be sorted in the order they were in the original header
        list, or were added to this instance, and may contain duplicates.
        Any fields deleted and re-inserted are always appended to the header
        list.
        """
        return self._headers[:]

    def __repr__(self):
        return "Headers(%s)" % `self._headers`

    def __str__(self):
        """str() returns the formatted headers, complete with end line,
        suitable for direct HTTP transmission."""
        return '\r\n'.join(["%s: %s" % kv for kv in self._headers]+['',''])

    def setdefault(self,name,value):
        """Return first matching header value for 'name', or 'value'

        If there is no header named 'name', add a new header with name 'name'
        and value 'value'."""
        result = self.get(name)
        if result is None:
            self._headers.append((name,value))
            return value
        else:
            return result

    def add_header(self, _name, _value, **_params):
        """Extended header setting.

        _name is the header field to add.  keyword arguments can be used to set
        additional parameters for the header field, with underscores converted
        to dashes.  Normally the parameter will be added as key="value" unless
        value is None, in which case only the key will be added.

        Example:

        h.add_header('content-disposition', 'attachment', filename='bud.gif')

        Note that unlike the corresponding 'email.Message' method, this does
        *not* handle '(charset, language, value)' tuples: all values must be
        strings or None.
        """
        parts = []
        if _value is not None:
            parts.append(_value)
        for k, v in _params.items():
            if v is None:
                parts.append(k.replace('_', '-'))
            else:
                parts.append(_formatparam(k.replace('_', '-'), v))
        self._headers.append((_name, "; ".join(parts)))



class ServerHandler(object):
    """Manage the invocation of a WSGI application"""

    # Configuration parameters; can override per-subclass or per-instance
    wsgi_version = (1,0)
    wsgi_multithread = True
    wsgi_multiprocess = True
    wsgi_run_once = False

    origin_server = True    # We are transmitting direct to client
    http_version  = "1.0"   # Version that should be used for response
    server_software = 'ECFHttpd/1.0'

    # os_environ is used to supply configuration from the OS environment:
    # by default it's a copy of 'os.environ' as of import time, but you can
    # override this in e.g. your __init__ method.
    os_environ = dict(os.environ.items())

    headers_class = Headers             # must be a Headers-like class

    # Error handling (also per-subclass or per-instance)
    traceback_limit = None  # Print entire traceback to self.get_stderr()
    error_status = "500 INTERNAL SERVER ERROR"
    error_headers = [('Content-Type','text/plain')]

    # State variables (don't mess with these)
    status = result = None
    headers_sent = False
    headers = None
    bytes_sent = 0

    def __init__(self, stdin, stdout, stderr, environ, multithread=True,
        multiprocess=False):
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.base_env = environ
        self.wsgi_multithread = multithread
        self.wsgi_multiprocess = multiprocess

    def run(self, application):
        """Invoke the application"""
        # Note to self: don't move the close()!  Asynchronous servers shouldn't
        # call close() from finish_response(), so if you close() anywhere but
        # the double-error branch here, you'll break asynchronous servers by
        # prematurely closing.  Async servers must return from 'run()' without
        # closing if there might still be output to iterate over.
        try:
            self.setup_environ()
            self.result = application(self.environ, self.start_response)
            self.finish_response()
        except:
            try:
                self.handle_error()
            except:
                # If we get an error handling an error, just give up already!
                self.close()
                raise   # ...and let the actual server figure it out.

    def setup_environ(self):
        """Set up the environment for one request"""

        env = self.environ = self.os_environ.copy()
        self.add_cgi_vars()

        env['wsgi.input']        = self.get_stdin()
        env['wsgi.errors']       = self.get_stderr()
        env['wsgi.version']      = self.wsgi_version
        env['wsgi.run_once']     = self.wsgi_run_once
        env['wsgi.url_scheme']   = self.get_scheme()
        env['wsgi.multithread']  = self.wsgi_multithread
        env['wsgi.multiprocess'] = self.wsgi_multiprocess

        # if self.wsgi_file_wrapper is not None:
        #     env['wsgi.file_wrapper'] = self.wsgi_file_wrapper

        if self.origin_server and self.server_software:
            env.setdefault('SERVER_SOFTWARE',self.server_software)

    def finish_response(self):
        """Send any iterable data, then close self and the iterable

        Subclasses intended for use in asynchronous servers will
        want to redefine this method, such that it sets up callbacks
        in the event loop to iterate over the data, and to call
        'self.close()' once the response is finished.
        """
        if not self.result_is_file() and not self.sendfile():
            for data in self.result:
                self.write(data)
            self.finish_content()
        self.close()

    def get_scheme(self):
        """Return the URL scheme being used"""
        return guess_scheme(self.environ)

    def set_content_length(self):
        """Compute Content-Length or switch to chunked encoding if possible"""
        try:
            blocks = len(self.result)
        except (TypeError, AttributeError, NotImplementedError):
            pass
        else:
            if blocks==1:
                self.headers['Content-Length'] = str(self.bytes_sent)
                return
        # XXX Try for chunked encoding if origin server and client is 1.1

    def cleanup_headers(self):
        """Make any necessary header changes or defaults

        Subclasses can extend this to add other defaults.
        """
        if 'Content-Length' not in self.headers:
            self.set_content_length()

    def start_response(self, status, headers,exc_info=None):
        """'start_response()' callable as specified by PEP 333"""

        if exc_info:
            try:
                if self.headers_sent:
                    # Re-raise original exception if headers sent
                    raise exc_info[0], exc_info[1], exc_info[2]
            finally:
                exc_info = None        # avoid dangling circular ref
        elif self.headers is not None:
            raise AssertionError("Headers already set!")

        assert isinstance(status, str),"Status must be a string"
        assert len(status)>=4,"Status must be at least 4 characters"
        assert int(status[:3]),"Status message must begin w/3-digit code"
        assert status[3]==" ", "Status message must have a space after code"
        if __debug__:
            for name,val in headers:
                assert isinstance(name, str),"Header names must be strings"
                assert isinstance(val, str),"Header values must be strings"
                assert not is_hop_by_hop(name),"Hop-by-hop headers not allowed"
        self.status = status
        self.headers = self.headers_class(headers)
        return self.write

    def send_preamble(self):
        """Transmit version/status/date/server, via self._write()"""
        if self.origin_server:
            if self.client_is_modern():
                self._write('HTTP/%s %s\r\n' % (self.http_version,self.status))
                if 'Date' not in self.headers:
                    self._write(
                        'Date: %s\r\n' % http_date()
                    )
                if self.server_software and 'Server' not in self.headers:
                    self._write('Server: %s\r\n' % self.server_software)
        else:
            self._write('Status: %s\r\n' % self.status)

    def write(self, data):
        """'write()' callable as specified by PEP 333"""

        assert isinstance(data, str), "write() argument must be string"

        if not self.status:
            raise AssertionError("write() before start_response()")

        elif not self.headers_sent:
            # Before the first output, send the stored headers
            self.bytes_sent = len(data)    # make sure we know content-length
            self.send_headers()
        else:
            self.bytes_sent += len(data)

        # XXX check Content-Length and truncate if too many bytes written?
        # If data is too large, socket will choke, so write chunks no larger
        # than 32MB at a time.
        length = len(data)
        if length > 33554432:
            offset = 0
            while offset < length:
                chunk_size = min(33554432, length)
                self._write(data[offset:offset+chunk_size])
                self._flush()
                offset += chunk_size
        else:
            self._write(data)
            self._flush()

    def sendfile(self):
        """Platform-specific file transmission

        Override this method in subclasses to support platform-specific
        file transmission.  It is only called if the application's
        return iterable ('self.result') is an instance of
        'self.wsgi_file_wrapper'.

        This method should return a true value if it was able to actually
        transmit the wrapped file-like object using a platform-specific
        approach.  It should return a false value if normal iteration
        should be used instead.  An exception can be raised to indicate
        that transmission was attempted, but failed.

        NOTE: this method should call 'self.send_headers()' if
        'self.headers_sent' is false and it is going to attempt direct
        transmission of the file1.
        """
        return False   # No platform-specific transmission by default

    def finish_content(self):
        """Ensure headers and content have both been sent"""
        if not self.headers_sent:
            self.headers['Content-Length'] = "0"
            self.send_headers()
        else:
            pass # XXX check if content-length was too short?

    def xx_close(self):
        try:
            self.request_handler.log_request(self.status.split(' ',1)[0], self.bytes_sent)
        finally:
            try:
                if hasattr(self.result,'close'):
                    self.result.close()
            finally:
                self.result = self.headers = self.status = self.environ = None
                self.bytes_sent = 0; self.headers_sent = False
    def close(self):
        try:
            if hasattr(self.result,'close'):
                self.result.close()
        finally:
            self.result = self.headers = self.status = self.environ = None
            self.bytes_sent = 0; self.headers_sent = False

    def send_headers(self):
        """Transmit headers to the client, via self._write()"""
        self.cleanup_headers()
        self.headers_sent = True
        if not self.origin_server or self.client_is_modern():
            self.send_preamble()
            self._write(str(self.headers))

    def result_is_file(self):
        """True if 'self.result' is an instance of 'self.wsgi_file_wrapper'"""
        # wrapper = self.wsgi_file_wrapper
        # return wrapper is not None and isinstance(self.result,wrapper)
        return False

    def client_is_modern(self):
        """True if client can accept status and headers"""
        return self.environ['SERVER_PROTOCOL'].upper() != 'HTTP/0.9'

    def log_exception(self,exc_info):
        """Log the 'exc_info' tuple in the server log

        Subclasses may override to retarget the output or change its format.
        """
        try:
            from traceback import print_exception
            stderr = self.get_stderr()
            print_exception(
                exc_info[0], exc_info[1], exc_info[2],
                self.traceback_limit, stderr
            )
            stderr.flush()
        finally:
            exc_info = None

    def handle_error(self):
        """Log current error, and send error output to client if possible"""
        self.log_exception(sys.exc_info())
        if not self.headers_sent:
            self.result = self.error_output(self.environ, self.start_response)
            self.finish_response()
        # XXX else: attempt advanced recovery techniques for HTML or text?

    def error_output(self, environ, start_response):
        import traceback
        start_response(self.error_status, self.error_headers[:], sys.exc_info())
        return ['\n'.join(traceback.format_exception(*sys.exc_info()))]

    # Pure abstract methods; *must* be overridden in subclasses

    def _write(self,data):
        self.stdout.write(data)
        self._write = self.stdout.write

    def _flush(self):
        self.stdout.flush()
        self._flush = self.stdout.flush

    def get_stdin(self):
        return self.stdin

    def get_stderr(self):
        return self.stderr

    def add_cgi_vars(self):
        self.environ.update(self.base_env)

class ECFWSGIServer:

  application = None

  def __init__(self, RequestHandlerClass, root_path, serveraddr, serverport):
    self.root_path = root_path
    self.server_address = serveraddr
    self.server_port = serverport
    self.RequestHandlerClass = RequestHandlerClass
    self.server_bind()

  def server_bind(self):
    """Override server_bind to store the server name."""
    self.server_name = socket.getfqdn(self.server_address)
    self.setup_environ()

  def setup_environ(self):
    # Set up base environment
    env = self.base_environ = {}
    env['SERVER_NAME'] = self.server_name
    env['SERVER_PORT'] = self.server_port
    env['GATEWAY_INTERFACE'] = 'CGI/1.1'
    env['REMOTE_HOST']=''
    env['CONTENT_LENGTH']=''
    env['SCRIPT_NAME'] = ''

  def get_app(self):
    return self.application

  def set_app(self,application):
    self.application = application

  def handle_request(self, __header, __body, __client_address):
    """Handle one request, possibly blocking."""
    resp = None
    if self.verify_request(__header, __body):
      try:
          resp = self.process_request(__header, __body, __client_address)
      except:
          self.handle_error()
          self.close_request()
    return resp

  def verify_request(self, __header, __body):
    """Verify the request.  May be overridden.

    Return True if we should proceed with this request.

    """
    return True

  def process_request(self, __header, __body, __client_address):
    """Call finish_request.

    Overridden by ForkingMixIn and ThreadingMixIn.

    """
    try:
      resp = self.finish_request(__header, __body, __client_address)
    finally:
      el.session.close()
      self.close_request()
    return resp

  def finish_request(self, __header, __body, __client_address):
    """Finish one request by instantiating RequestHandlerClass."""
    req_handle = self.RequestHandlerClass(__header, __body, __client_address, self)
    req_handle.wfile.flush()
    resp = req_handle.wfile.getvalue()
    req_handle.wfile.close()
    return resp

  def close_request(self):
    """Called to clean up an individual request."""
    pass

  def handle_error(self):
    """Handle an error gracefully.  May be overridden.

    The default is to print a traceback and continue.

    """
    print '-'*40
    print 'Exception happened during processing of request from',
    import traceback
    traceback.print_exc() # XXX But this goes to stderr!
    print '-'*40


def setup_mimetypes(rootpath):
  mime_path = os.path.join(os.path.abspath(rootpath), "mime.types")
  mimetypes.init([mime_path])

def make_server_handler(wsgi_app, serveraddr, serverport):
  root_path = os.path.abspath(os.path.dirname(wsgi_app))
  sys.path.append(root_path)
  full_name = os.path.split(wsgi_app)[1]
  wsgi_mod = full_name.split('.')[0]
  the_app = __import__(wsgi_mod, globals(), locals())
  application = getattr(the_app, 'application', None)
  wsgi_server = ECFWSGIServer(ECFWSGIRequestHandler, root_path, serveraddr, serverport)
  wsgi_server.set_app(application)
  return wsgi_server
