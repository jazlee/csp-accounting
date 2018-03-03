# KInterbasDB Python Package - Type Conv : DateTime/Python 2.3+ Standard Library
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

__all__ = (
    # kinterbasdb-native date and time converters:
    'date_conv_in', 'date_conv_out',
    'time_conv_in', 'time_conv_out',
    'timestamp_conv_in', 'timestamp_conv_out',

    # DB API 2.0 standard date and time type constructors:
    'Date', 'Time', 'Timestamp',
    'DateFromTicks', 'TimeFromTicks', 'TimestampFromTicks',
  )

from kinterbasdb.k_exceptions import *

# THIS CONVERSION MODULE IS NOT EXPECTED TO WORK WITH < PYTHON 2.3,
# since it uses the standard datetime module for its date/time operations.
import datetime as dt

################################################################################
## DATE AND TIME
################################################################################

# kinterbasdb-native date and time converters:
def date_conv_in(dtObj):
    # Allow implicit param conv:
    if dtObj is None or isinstance(dtObj, basestring):
        return dtObj

    if not isinstance(dtObj, dt.date):
        raise InterfaceError(
            'Required type: %s ; supplied type: %s'
            % ( str(dt.date), str(type(dtObj)) )
          )
    return dtObj.timetuple()[:3]

def date_conv_out(dateTuple):
    if dateTuple is None:
        return None
    return dt.date(*dateTuple)


def time_conv_in(tmObj):
    # Allow implicit param conv:
    if tmObj is None or isinstance(tmObj, basestring):
        return tmObj

    if not isinstance(tmObj, dt.time):
        raise InterfaceError(
            'Required type: %s ; supplied type: %s'
            % ( str(dt.time), str(type(tmObj)) )
          )
    timeTuple = (tmObj.hour, tmObj.minute, tmObj.second, tmObj.microsecond)
    return timeTuple

def time_conv_out(timeTuple):
    if timeTuple is None:
        return None
    return dt.time(*timeTuple)


def timestamp_conv_in(tsObj):
    # Allow implicit param conv:
    if tsObj is None or isinstance(tsObj, basestring):
        return tsObj

    if not isinstance(tsObj, dt.datetime):
        raise InterfaceError(
            'Required type: %s ; supplied type: %s'
            % ( str(dt.datetime), str(type(tsObj)) )
          )

    timestampTuple = (
        tsObj.year, tsObj.month, tsObj.day,
        tsObj.hour, tsObj.minute, tsObj.second, tsObj.microsecond
      )
    return timestampTuple

def timestamp_conv_out(timestampTuple):
    if timestampTuple is None:
        return None
    return dt.datetime(*timestampTuple)


# DB API 2.0 standard date and time type constructors:
def _makeFilteredConstructor(underlyingConstructor):
    def Constructor(*args, **kwargs):
        try:
            return underlyingConstructor(*args, **kwargs)
        except ValueError, e:
            raise DataError(str(e))
    return Constructor

Date = _makeFilteredConstructor(dt.date)
Time = _makeFilteredConstructor(dt.time)
Timestamp = _makeFilteredConstructor(dt.datetime)

DateFromTicks = _makeFilteredConstructor(dt.date.fromtimestamp)
TimeFromTicks = _makeFilteredConstructor(lambda ticks: TimestampFromTicks(ticks).time())
TimestampFromTicks = _makeFilteredConstructor(dt.datetime.fromtimestamp)
