# KInterbasDB Python Package - Type Conv : Fixed/Standard Library
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

__all__ = (
    # kinterbasdb-native fixed point converters (old, precison_mode style):
    'fixed_conv_in_imprecise', 'fixed_conv_in_precise',
    'fixed_conv_out_imprecise', 'fixed_conv_out_precise',
  )

import sys
from kinterbasdb.k_exceptions import *

################################################################################
## FIXED POINT
################################################################################

_tenTo = [10**x for x in range(20)]
del x

# The fixed point input funcions are GUARANTEED to receive a single parameter
# that is a 2-tuple of the form: (original input object, scale).
# The original input object may, of course, be None.
def fixed_conv_in_imprecise((val, scale)):
    if val is None or isinstance(val, basestring): # Allow implicit param conv.
        return val
    if not isinstance(val, (float, int, long)):
        raise InterfaceError(
            'float required as input for fixed point field in imprecise mode.'
          )
    absScale = abs(scale)
    return int(round(val, absScale) * _tenTo[absScale])

def fixed_conv_in_precise((val, scale)):
    if val is None or isinstance(val, basestring): # Allow implicit param conv.
        return val
    if not isinstance(val, (int, long)):
        raise InterfaceError(
            'int or long required as input for fixed point field in precise mode.'
          )
    # $val is already a scaled integer; just pass it through.
    return val


# The fixed point output funcions receive a single parameter that is either
# - None (if the SQL value is NULL), or
# - a 2-tuple of the form: (scaled integer value, scale)
def fixed_conv_out_imprecise(x):
    # Return a floating point representation of the scaled integer.
    if x is None:
        return None
    (val, scale) = x
    if scale == 0:
        return val # Don't convert to float if no decimal places.
    return float(val) / _tenTo[abs(scale)]

def fixed_conv_out_precise(x):
    # Simply return the scaled integer, not interpreted in any way.
    if x is None:
        return None
    return x[0]
