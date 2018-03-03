# KInterbasDB Python Package - Type Conv : DateTime/Minimal
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
    # kinterbasdb-native date and time converters:
    'date_conv_in', 'date_conv_out',
    'time_conv_in', 'time_conv_out',
    'timestamp_conv_in', 'timestamp_conv_out',

    # DB API 2.0 standard date and time type constructors:
    'Date', 'Time', 'Timestamp',
    'DateFromTicks', 'TimeFromTicks', 'TimestampFromTicks',
  )

import sys, time
from kinterbasdb.k_exceptions import *

################################################################################
## DATE AND TIME
################################################################################

# kinterbasdb-native date and time converters:
def date_conv_in(dateObj):
    # Allow implicit param conv from string:
    if dateObj is None or isinstance(dateObj, basestring):
        return dateObj

    if not isinstance(dateObj, tuple):
        raise InterfaceError(
            'Cannot convert object of type %s to native kinterbasdb tuple.'
            % str(type(dateObj))
          )
    return dateObj

def date_conv_out(dateTuple):
    return dateTuple


def time_conv_in(timeObj):
    # Allow implicit param conv from string:
    if timeObj is None or isinstance(timeObj, basestring):
        return timeObj

    if not isinstance(timeObj, tuple):
        raise InterfaceError(
            'Cannot convert object of type %s to native kinterbasdb tuple.'
            % str(type(timeObj))
          )
    return timeObj

def time_conv_out(timeTuple):
    return timeTuple


def timestamp_conv_in(timestampObj):
    # Allow implicit param conv from string:
    if timestampObj is None or isinstance(timestampObj, basestring):
        return timestampObj

    if not isinstance(timestampObj, tuple):
        raise InterfaceError(
            'Cannot convert object of type %s to native kinterbasdb tuple.'
            % str(type(timestampObj))
          )

    return timestampObj

def timestamp_conv_out(timestampTuple):
    return timestampTuple


# DB API 2.0 standard date and time type constructors:
def Date(year, month, day):
    return (year, month, day)

def Time(hour, minute, second):
    return (hour, minute, second)

def Timestamp(year, month, day, hour, minute, second):
    return (year, month, day, hour, minute, second)

def DateFromTicks(ticks):
    return time.localtime(ticks)[:3]

def TimeFromTicks(ticks):
    return time.localtime(ticks)[3:6]

def TimestampFromTicks(ticks):
    return time.localtime(ticks)[:6]
