# vim:set et ts=4 sw=4 ai ft=python:

"""
Simple function call on an interval (similar to setInterval in javascript)

Usage:

    import timeinterval
    stopper = timeinterval.start(milliseconds, function, arg1, kw=arg2...)

    # later:
    stopper.stop()

------------------------------------------------------------------

Copyright 2016 Brandon Gillespie

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""

import threading
import traceback
import logging

__version__ = 1.0

################################################################################
def start(milliseconds, func, *args, **kwargs):
    """
    Call function every interval.  Starts the timer at call time.
    Although this could also be a decorator, that would not initiate the time at
    the same time, so would require additional work.

    Arguments following function will be sent to function.  Note that these args
    are part of the defining state, and unless it is an object will reset each
    interval.

    The inine test will print "TickTock x.." every second, where x increments.

    >>> import time
    >>> class Tock(object):
    ...     count = 0
    ...     stop = None
    >>> def tick(obj):
    ...     obj.count += 1
    ...     if obj.stop and obj.count == 4:
    ...         obj.stop.set() # shut itself off
    ...         return
    ...     print("TickTock {}..".format(obj.count))
    >>> tock = Tock()
    >>> tock.stop = start(1000, tick, tock)
    >>> time.sleep(6)
    TickTock 1..
    TickTock 2..
    TickTock 3..
    """

    stopper = threading.Event()
    def interval(seconds, func, *args, **kwargs):
        """outer wrapper"""
        def wrapper():
            """inner wrapper"""
            if stopper.isSet():
                return
            interval(seconds, func, *args, **kwargs)
            try:
                func(*args, **kwargs)
            except: # pylint: disable=bare-except
                logging.error("Error during interval")
                logging.error(traceback.format_exc())

        thread = threading.Timer(seconds, wrapper)
        thread.daemon = True
        thread.start()
    interval(milliseconds/1000, func, *args, **kwargs)
    return stopper

