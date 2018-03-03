# KInterbasDB Python Package - Type Conv : Even More Progressive
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
#   2002-2004 [dsr]   David Rushby          <woodsplitter@rocketmail.com>
# [Contributors:]
#   2001      [eac]   Evgeny A. Cherkashin  <eugeneai@icc.ru>
#   2001-2002 [janez] Janez Jere            <janez.jere@void.si>

# This module can be conveniently activated as the process-wide default via:
#   kinterbasdb.init(type_conv=199)
#
# This module represents date/time values via datetime, and fixed point values
# (imprecisely) as floats.  It is designed *solely* for client programs that
# want to use the standard library datetime module for date/time values, but
# don't care about the representation of fixed point values and don't want to
# pay the substantial memory overhead for importing the standard library
# decimal module.
#
# !!IF YOU CARE ABOUT THE PRECISION OF NUMERIC AND DECIMAL VALUES, DO NOT USE
# THIS MODULE; USE THE typeconv_24plus MODULE INSTEAD!!  typeconv_24plus can be
# conveniently activated as the process-wide default via:
#   kinterbasdb.init(type_conv=200)

from kinterbasdb import typeconv_datetime_stdlib
from kinterbasdb import typeconv_fixed_stdlib # uses floats, not Decimals
from kinterbasdb import typeconv_text_unicode

_underlying_modules = (
    typeconv_datetime_stdlib,
    typeconv_fixed_stdlib,
    typeconv_text_unicode
  )

# Load the required members from the underlying modules into the namespace of
# this module.
globalz = globals()
for m in _underlying_modules:
    for req_member in m.__all__:
        globalz[req_member] = getattr(m, req_member)
del globalz
