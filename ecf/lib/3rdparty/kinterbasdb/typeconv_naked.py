# KInterbasDB Python Package - Type Conv : Minimal
#
# Version 3.1
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
#   kinterbasdb.init(type_conv=0)

from kinterbasdb import typeconv_datetime_naked
from kinterbasdb import typeconv_fixed_stdlib

_underlying_modules = (typeconv_datetime_naked, typeconv_fixed_stdlib)

# Load the required members from the underlying modules into the namespace of
# this module.
globalz = globals()
for m in _underlying_modules:
    for req_member in m.__all__:
        globalz[req_member] = getattr(m, req_member)
del globalz
