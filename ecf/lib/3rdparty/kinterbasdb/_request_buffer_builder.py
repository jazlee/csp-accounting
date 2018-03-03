# KInterbasDB Python Package - Request Buffer Builder
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

# This module is private.

import struct

# __init__.py will fill this with a function reference when it imports this
# module:
portable_int = None

class RequestBufferBuilder(object):
    def __init__(self, clusterIdentifier=None):
        self.clear()

        if clusterIdentifier:
            self._addCode(clusterIdentifier)

    def render(self):
        # Convert the RequestBufferBuilder's components to a binary Python str.
        return ''.join(self._buffer)

    def clear(self):
        self._buffer = []

    def _extend(self, otherRequestBuilder):
        self._buffer.append(otherRequestBuilder.render())

    def _addRaw(self, rawBuf):
        assert isinstance(rawBuf, str)
        self._buffer.append(rawBuf)

    def _addCode(self, code):
        _code2reqbuf(self._buffer, code)

    def _addString(self, code, s):
        _string2reqbuf(self._buffer, code, s)

    def _addNumeric(self, code, n, numCType='I'):
        _numeric2reqbuf(self._buffer, code, n, numCType=numCType)

def _vax_inverse(i, format):
    # Apply the inverse of isc_vax_integer to a Python integer; return
    # the raw bytes of the resulting value.
    iRaw = struct.pack(format, i)
    iConv = portable_int(iRaw)
    iConvRaw = struct.pack(format, iConv)
    return iConvRaw

def _renderSizedIntegerForSPB(i, format):
    #   In order to prepare the Python integer i for inclusion in a request
    # buffer, the byte sequence of i must be reversed, which will make i
    # unrepresentible as a normal Python integer.
    #   Therefore, the rendered version of i must be stored in a raw byte
    # buffer.
    #   This function returns a 2-tuple containing:
    # 1. the calculated struct.pack-compatible format string for i
    # 2. the Python string containing the SPB-compatible raw binary rendering
    #    of i
    #
    # Example:
    # To prepare the Python integer 12345 for storage as an unsigned int in a
    # request buffer, use code such as this:
    #   (iPackFormat, iRawBytes) = _renderSizedIntegerForSPB(12345, 'I')
    #   spbBytes = struct.pack(iPackFormat, iRawBytes)
    #
    destFormat = '%ds' % struct.calcsize(format)
    destVal = _vax_inverse(i,  format)
    return (destFormat, destVal)

def _string2reqbuf(reqBuf, code, s):
    sLen = len(s)

    _numeric2reqbuf(reqBuf, code, sLen, numCType='H')

    format = str(sLen) + 's' # The length, then 's'.
    reqBuf.append( struct.pack(format, s) )

def _numeric2reqbuf(reqBuf, code, num, numCType='I'):
    # numCType is one of the pack format characters specified by the Python
    # standard library module 'struct'.
    _code2reqbuf(reqBuf, code)

    (numericFormat, numericBytes) = _renderSizedIntegerForSPB(num, numCType)
    reqBuf.append( struct.pack(numericFormat, numericBytes) )

def _code2reqbuf(reqBuf, code):
    if isinstance(code, str):
        assert len(code) == 1
        code = ord(code)

    # The database engine considers little-endian integers "portable"; they
    # need to have been converted to little-endianness before being sent across
    # the network.
    reqBuf.append(struct.pack('<b', code))
