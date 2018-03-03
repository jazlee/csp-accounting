# KInterbasDB Python Package - Type Conv : DateTime/eGenix mx.DateTime
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

import sys
from kinterbasdb.k_exceptions import *

# This conversion module uses mx.DateTime for its date/time operations.
try:
    from mx import DateTime as mxDT
except ImportError:
    raise ImportError('kinterbasdb uses the mx.DateTime module (from the'
        ' "eGenix mx Base Package") by default for date/time/timestamp'
        ' representation, but you do not have this package installed.'
        '\nYou can either download the eGenix mx Base Package from'
        '\nhttp://www.egenix.com/files/python/eGenix-mx-Extensions.html#Download-mxBASE'
        '\nor tell kinterbasdb to use the Python standard library datetime'
        ' module instead, as explained at'
        '\nhttp://kinterbasdb.sourceforge.net/dist_docs/usage.html#faq_fep_is_mxdatetime_required'
      )

################################################################################
## DATE AND TIME
################################################################################

# kinterbasdb-native date and time converters:
def date_conv_in(mxDateTimeObj):
    # Allow implicit param conv:
    if mxDateTimeObj is None or isinstance(mxDateTimeObj, basestring):
        return mxDateTimeObj

    if not isinstance(mxDateTimeObj, mxDT.DateTimeType):
        raise InterfaceError(
            'Required type: %s ; supplied type: %s'
            % ( str(mxDT.DateTimeType), str(type(mxDateTimeObj)) )
          )
    return mxDateTimeObj.tuple()[:3]

def date_conv_out(dateTuple):
    if dateTuple is None:
        return None
    return mxDT.DateTime(*dateTuple)


def time_conv_in(mxDateTimeOrTimeDeltaObj):
    # Allow implicit param conv:
    if (    mxDateTimeOrTimeDeltaObj is None
         or isinstance(mxDateTimeOrTimeDeltaObj, basestring)
      ):
        return mxDateTimeOrTimeDeltaObj

    if isinstance(mxDateTimeOrTimeDeltaObj, mxDT.DateTimeType):
        timeTuple = mxDateTimeOrTimeDeltaObj.tuple()[3:6]
    elif isinstance(mxDateTimeOrTimeDeltaObj, mxDT.DateTimeDeltaType):
        timeTuple = mxDateTimeOrTimeDeltaObj.tuple()[1:]
    else:
        raise InterfaceError(
            'Cannot convert object of type %s to native kinterbasdb tuple.'
            % str(type(mxDateTimeOrTimeDeltaObj))
          )

    secondsFrac = timeTuple[2]
    seconds = int(secondsFrac)
    microseconds = int((secondsFrac - seconds) * 1000000)

    return (timeTuple[0], timeTuple[1], seconds, microseconds)

def time_conv_out(timeTuple):
    if timeTuple is None:
        return None

    if len(timeTuple) != 4:
        return mxDT.Time(*timeTuple)
    else:
        (hour, minute, second, micros) = timeTuple
        secondsFrac = second + micros / 1000000.0

        return mxDT.Time(hour, minute, secondsFrac)


def timestamp_conv_in(mxDateTimeObj):
    # Allow implicit param conv:
    if mxDateTimeObj is None or isinstance(mxDateTimeObj, basestring):
        return mxDateTimeObj

    if not isinstance(mxDateTimeObj, mxDT.DateTimeType):
        raise InterfaceError(
            'Required type: %s ; supplied type: %s'
            % ( str(mxDT.DateTimeType), str(type(mxDateTimeObj)) )
          )

    timestampTuple = mxDateTimeObj.tuple()

    secondsFrac = timestampTuple[5]
    seconds = int(secondsFrac)
    microseconds = int((secondsFrac - seconds) * 1000000)

    return timestampTuple[:5] + (seconds, microseconds)

def timestamp_conv_out(timestampTuple):
    if timestampTuple is None:
        return None

    if len(timestampTuple) == 7:
        (year, month, day, hour, minute, second, micros) = timestampTuple
        secondsFrac = second + micros / 1000000.0
    else:
        (year, month, day, hour, minute, second) = timestampTuple
        secondsFrac = second

    return mxDT.DateTime(year, month, day, hour, minute, secondsFrac)


# DB API 2.0 standard date and time type constructors:
def Date(year, month, day):
    try:
        theDate = mxDT.DateTime(year, month, day)
    except mxDT.Error, e:
        raise DataError(str(e))

    return theDate


def Time(hour, minute, second):
    # mx DateTimeDeltas roll over when provided with an hour greater than
    # 23, a minute greater than 59, and so on.  That is not acceptable for our
    # purposes.
    if hour < 0 or hour > 23:
        raise DataError("hour must be between 0 and 23")
    if minute < 0 or minute > 59:
        raise DataError("minute must be between 0 and 59")
    if second < 0 or second > 59:
        raise DataError("second must be between 0 and 59")

    try:
        theTime = mxDT.TimeDelta(hour, minute, second)
    except mxDT.Error, e:
        raise DataError(str(e))

    return theTime


def Timestamp(year, month, day, hour, minute, second):
    args = (year, month, day, hour, minute, second) # Yes, I know about the
      # *args syntactical shortcut, but it's not particularly readable.

    # mx mxDT's Timestamp constructor accepts negative values in the
    # spirit of Python's negative list indexes, but I see no reason to allow
    # that behavior in this DB API-compliance-obsessed module.
    if 0 < len(filter(lambda x: x < 0, args)):
        raise DataError("Values less than zero not allowed in Timestamp."
            " (Received arguments %s)"
            % repr(args)
          )

    try:
        theStamp = mxDT.DateTime(*args)
    except mxDT.Error, e:
        raise DataError(str(e))

    return theStamp


DateFromTicks = mxDT.DateFromTicks
TimeFromTicks = mxDT.TimeFromTicks
TimestampFromTicks = mxDT.TimestampFromTicks
