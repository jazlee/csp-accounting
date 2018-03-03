# KInterbasDB Python Package - Python Wrapper for Core
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

import threading


_lock = threading.Lock()
_objects = {}


def startTimeoutThreadIfNecessary(cttMain, cttStopFunc):
    _lock.acquire()
    try:
        if 'ctt' not in _objects:
            startedEvent = threading.Event()

            # Start the CTT:
            ctt = ConnectionTimeoutThread(cttMain, startedEvent)
            ctt.start()
            _objects['ctt'] = ctt

            # Wait for the CTT to indicate that it has finished starting:
            startedEvent.wait()
            del startedEvent

            _objects['stopFunc'] = cttStopFunc
    finally:
        _lock.release()


def isTimeoutThreadStarted():
    _lock.acquire()
    try:
        return 'ctt' in _objects
    finally:
        _lock.release()


def stopConnectionTimeoutThread():
    _lock.acquire()
    try:
        _objects['stopFunc']()
        assert not _objects['ctt'].isAlive()
        _objects.clear()
    finally:
        _lock.release()


class ConnectionTimeoutThread(threading.Thread):
    # This class exists to facilitate:
    #   - Proper bootstrapping of Python thread state onto the
    #     ConnectionTimeoutThread.
    #   - Communication between Python code and the ConnectionTimeoutThread.
    #
    # All of the "real functionality" of the ConnectionTimeoutThread is written
    # in C, and most of it executes with the GIL released.
    def __init__(self, cttMain, startedEvent):
        threading.Thread.__init__(self, name='kinterbasdb_ConTimeoutThread')
        self.setDaemon(True)

        self._cttMain = cttMain
        self._startedEvent = startedEvent

    def run(self):
        startedEvent = self._startedEvent
        del self._startedEvent
        cttMain = self._cttMain
        del self._cttMain
        cttMain(self, startedEvent)
