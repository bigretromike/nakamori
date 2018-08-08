#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cProfile
import pstats
import xbmc
import nakamoritools as nt

has_pydev = False
has_line_profiler = False
try:
    # noinspection PyUnresolvedReferences
    import line_profiler
    has_line_profiler = True
except ImportError:
    pass

try:
    # noinspection PyUnresolvedReferences
    import pydevd
    has_pydev = True
except ImportError:
    pass


def profile_this(func):
    """
    This can be used to profile any function.
    Usage:
    @profile_this
    def function_to_profile(arg, arg2):
        pass
    """

    def profiled_func(*args, **kwargs):
        """
        a small wrapper
        """
        profile = cProfile.Profile()
        try:
            profile.enable()
            result = func(*args, **kwargs)
            profile.disable()
            return result
        finally:
            stream = nt.StringIO()
            sortby = 'time'
            ps = pstats.Stats(profile, stream=stream).sort_stats(sortby)
            ps.print_stats()
            xbmc.log('Profiled Function: ' + func.__name__ + '\n' + stream.getvalue(), xbmc.LOGWARNING)
    return profiled_func