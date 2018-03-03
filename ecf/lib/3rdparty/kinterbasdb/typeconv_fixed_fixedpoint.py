# KInterbasDB Python Package - Type Conv : Fixed/fixedpoint Module (3rd-party)
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

# The fixedpoint module resides at:  http://fixedpoint.sourceforge.net/
from fixedpoint import FixedPoint

from kinterbasdb.k_exceptions import *


_tenTo = [10**x for x in range(20)]
del x


################################################################################
## FIXED POINT
################################################################################

def fixed_conv_in_precise((val, scale)):
    # Allow implicit param conv:
    if val is None or isinstance(val, basestring):
        return val

    return int(val * _tenTo[abs(scale)])

fixed_conv_in_imprecise = fixed_conv_in_precise


def fixed_conv_out_precise(x):
    if x is None:
        return None
    absScale = abs(x[1])
    return FixedPoint(x[0], absScale) / _tenTo[absScale]

fixed_conv_out_imprecise = fixed_conv_out_precise
