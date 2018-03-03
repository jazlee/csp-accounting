# KInterbasDB Python Package - Type Conv : Fixed/Python 2.4+ Standard Library
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

# We import the decimal module lazily so that client programs that use
# kinterbasdb.init(type_conv=200), but don't actually use any fixed point
# fields, don't pay the rather large memory overhead of the decimal module.
Decimal = None

from kinterbasdb.k_exceptions import *


_tenTo = [10**x for x in range(20)]
del x

_passThroughTypes = (
    type(None),
    str, # str, not basestring, for implicit param conv.
  )

_simpleScaleTypes = (
    int, long, float,
  )


################################################################################
## FIXED POINT
################################################################################

def fixed_conv_in_precise((val, scale)):
    global Decimal
    if Decimal is None:
        from decimal import Decimal

    if isinstance(val, _passThroughTypes):
        res = val
    elif isinstance(val, Decimal):
        # Input conversion process:
        #   1. Scale val up by the appropriate power of ten
        #      -> Decimal object
        #   2. Ask the resulting Decimal object to represent itself as an
        #      integral, which will invoke whatever rounding policy happens to
        #      be in place
        #      -> Decimal object
        #   3. Convert the result of the previous step to an int (or a long, if
        #      the number is too large to fit into a native integer).
        #      -> int or long
        #
        # Note:
        #   The final step would not be compatible with Python < 2.3 when
        # handling large numbers (the int function in < 2.3 would raise an
        # exception if the number couldn't fit into a native integer).  Since
        # the decimal module didn't appear until 2.4 and kinterbasdb 3.2 will
        # not officially support < 2.3, this is not a problem.
        res = int((val * _tenTo[abs(scale)]).to_integral())
    elif isinstance(val, _simpleScaleTypes):
        res = int(val * _tenTo[abs(scale)])
    else:
        raise TypeError('Objects of type %s are not acceptable input for'
            ' a fixed-point column.' % str(type(val))
          )

    return res

fixed_conv_in_imprecise = fixed_conv_in_precise


def fixed_conv_out_precise(x):
    global Decimal
    if Decimal is None:
        from decimal import Decimal

    if x is None:
        return None
    # x[0] is an integer or long, and we divide it by a power of ten, so we're
    # assured a lossless result:
    return Decimal(x[0]) / _tenTo[abs(x[1])]

fixed_conv_out_imprecise = fixed_conv_out_precise
